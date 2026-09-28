// Cloudflare Workers entrypoint. Generated policy stays outside public assets.
import policy from './policy.json';

const publicPaths = new Set(policy.paths);
const headers = {
  'Content-Security-Policy': "frame-ancestors 'none'; base-uri 'self'; object-src 'none'",
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};

function secure(response, request) {
  const result = new Response(request.method === 'HEAD' ? null : response.body, response);
  for (const [key, value] of Object.entries(headers)) result.headers.set(key, value);
  return result;
}

export default {
  async fetch(request, env) {
    const reply = (status, text, extra = {}) => secure(new Response(text, {
      status, headers: {'Cache-Control': 'no-store', ...extra},
    }), request);
    const url = new URL(request.url);
    // Compare the raw encoded path against build output; never serve arbitrary files.
    const isInquiry = policy.inquiryPath && url.pathname === policy.inquiryPath;
    if (!isInquiry && !publicPaths.has(url.pathname)) return reply(404, 'Not found');
    if (isInquiry ? request.method !== 'POST' : !['GET', 'HEAD'].includes(request.method)) {
      return reply(405, 'Method not allowed', {Allow: isInquiry ? 'POST' : 'GET, HEAD'});
    }
    if (isInquiry && (request.headers.get('Origin') !== url.origin ||
        request.headers.get('Content-Type')?.split(';')[0].trim() !== 'application/json')) {
      return reply(403, 'Invalid inquiry request');
    }
    // Only edge-provided verification is trusted. User-Agent and client headers confer no bypass.
    const verified = request.cf?.botManagement?.verifiedBot === true;
    const ip = request.headers.get('CF-Connecting-IP');
    if (isInquiry || !verified) {
      try {
        if (!ip) throw new Error('missing edge identity');
        const limiter = isInquiry ? env.INQUIRY_LIMITER : env.READ_LIMITER;
        const {success} = await limiter.limit({key: policy.siteId + ':' + ip});
        if (!success) return reply(429, 'Please retry later', {'Retry-After': '60'});
      } catch {
        // ponytail: public reads fail open for crawler availability; monitor and repair binding failures.
        console.warn('site-protection: rate limiter unavailable');
        if (isInquiry) return reply(503, 'Inquiry temporarily unavailable', {'Retry-After': '60'});
        const result = secure(await env.ASSETS.fetch(request), request);
        result.headers.set('X-Site-Protection', 'degraded');
        return result;
      }
    }
    if (isInquiry) {
      if (!env.INQUIRY) return reply(503, 'Inquiry service is not connected');
      // Cap streamed bodies too; Content-Length alone is not a trust boundary.
      const reader = request.body?.getReader();
      if (!reader) return reply(400, 'Missing inquiry');
      const chunks = []; let length = 0;
      for (;;) {
        const {done, value} = await reader.read();
        if (done) break;
        length += value.length;
        if (length > 16384) { await reader.cancel(); return reply(413, 'Inquiry too large'); }
        chunks.push(value);
      }
      const body = new Uint8Array(length); let offset = 0;
      for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
      try {
        const upstream = await env.INQUIRY.fetch(new Request(request, {body}));
        const result = secure(upstream, request);
        result.headers.set('Cache-Control', 'no-store');
        return result;
      } catch { return reply(503, 'Inquiry temporarily unavailable'); }
    }
    // Identical static content for buyers and crawlers; no challenge or cloaking.
    return secure(await env.ASSETS.fetch(request), request);
  },
};
