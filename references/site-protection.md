# 默认站点防护 · V2.2

每个行业、每次 draft/release 构建默认生成防护发布包，无需用户另行提出。公开网页能被浏览就能被复制；目标是提高批量抓取、镜像嵌套和接口滥用成本，保护未公开资料与真实询盘，同时保持正常搜索可达。不能保证禁止复刻、挡住分布式低速抓取，或保证所有平台收录。

## 生成与部署

编译器返回 `site_directory` 与 `deployment_directory`。后者位于 `private/deploy/edge-*/`，含 Worker、公开路径清单与 Wrangler 配置；**只有配置引用的 site_directory 作为静态资产上传**，整个企业项目和部署目录都不能当公共文件夹上传。

默认适配 Cloudflare Workers Static Assets：安装/使用当前受支持的 Wrangler，在本次部署目录运行 `wrangler deploy --dry-run` 检查包，按现有发布授权运行 `wrangler deploy`，绑定实际已批准域名。生成配置不附带账号凭据，不自动修改 DNS、不自动部署，也不迁移已有站点。Worker 名称由公司 ID 稳定派生；同公司多站点在首次部署时分别设置唯一名称与限流 namespace，重建沿用实际部署配置。`run_worker_first=true` 必须保留；仅上传静态 HTML 不会启用边缘防护。Worker 请求有平台用量/费用约束，部署时核对账号套餐。

所有改版及其他主机（Pages、Vercel、Nginx 等）也默认落实相同防护目标，由 Agent 在现有服务器/WAF中实现和验证，不强制迁移、不把 Workers 配置直接当 Pages 配置使用。已有框架动态路径须单独列入受控路由；不能用本静态文件白名单覆盖原应用后端。

## 默认运行行为

- 只允许构建清单内的 HTML、CSS、JS、图片、公开 PDF 与搜索文件。未知路径直接404，不能探测 `.env`、`.git`、私有知识卡或源码包；公开投影与许可/哈希检查仍是第一道边界。重新构建/部署完整包后旧文件自然不在清单，已有CDN和旧部署另行撤下。
- 公开读请求支持 GET/HEAD，所有访客获得同一内容。默认匿名每IP、每边缘位置约300次/60秒，超量429 + Retry-After:60 + no-store，暂不永久封IP。这是可调整的起点；共享办公出口、大型目录和合法爬虫需根据实际429调优。IP是匿名站点的粗粒度退让方案，可能影响共享出口，无法识别人；原生计数最终一致，不是精确全局配额。
- 只有 Cloudflare 提供的 `request.cf.botManagement.verifiedBot===true` 才豁免公开读取限流。该字段依赖 Bot Management 可用性；缺失时正常按宽松额度访问，不能假定所有套餐具备认证爬虫豁免。UA、Referer、客户端自报头、云厂商 ASN 都不能作为身份认证。不要直接拦截未知bot、无Referer、海外IP或无Cookie访客。
- 默认禁止跨站 iframe 嵌套（CSP frame-ancestors + X-Frame-Options），附 nosniff、严格来源策略。它限制镜像嵌套，不防止下载后重建。保留正文选择、复制、键盘操作、无JS阅读及图片搜索，不做正文加密、禁右键、全站登录/挑战或按bot输出不同正文。合法嵌入需求出现时修改具体 frame-ancestors 来源并同步调整 X-Frame-Options。
- 版权标识与既有 canonical 提供品牌/来源线索，私有素材台账保留原件哈希；它们不保证版权归属裁定或防复制。完整原图、生产文件、未公开规格、客户文件不发布；水印仅在拥有权利且不妨碍产品判断时另做公开衍生图，不能替代访问控制。不默认按Referer拦截热链，以免误伤图片搜索和AI读取。
- 读限流绑定异常时优先保持公开内容可达，响应 `X-Site-Protection: degraded` 并记录不含IP的告警；修复前防护验收不能PASS。询盘限流异常则503，不能假装接收成功。其他基础设施异常使用平台监控处理。

## 询盘接口边界

默认邮件草稿无需接收后端。`http` 同源端点在边缘仅接受同源Origin的JSON POST，约5次/IP/60秒、请求体最大16KiB（流式也受限），响应不缓存；爬虫身份不豁免写入。配置 `INQUIRY` Worker service binding 指向真实接收服务后才转交。未连接返回503，不返回演示成功。边缘不会读取或记录正文、发送邮件、保存CRM。

接收服务仍须独立验证字段、垃圾内容、持久存储、幂等/重试以及真实回执；不能将前端honeypot视作安全边界。只允许通过受保护入口访问服务，关闭或同样保护服务的workers.dev/直接入口；必要时按实际攻击增加Turnstile并在服务端验证，仅用于提交行为。外部HTTPS询盘端点不经过本站Worker，必须单独完成同等防护与CORS/回执验收，状态单独记录。

已有真实接收Worker时，在生成的wrangler.json合并 `"services": [{"binding": "INQUIRY", "service": "实际接收Worker名称"}]`，核对路由路径契约并记录配置差异。示例名称不能直接上线；服务不可用时保持失败提示和邮件入口。

## 搜索和 AI 访问

release 保持 robots、sitemap、canonical、正文/结构化数据一致；draft 仍noindex。训练政策沿用显式项目选择，不因防复制而默认拒绝所有AI爬虫。OAI-SearchBot、GPTBot、ChatGPT-User职责不同；Google/Bing/Perplexity及后续平台按当时官方文档和实际日志分别核验。允许读取不是承诺被引用。

部署时检查 Cloudflare 账号/域名已有的 Block AI bots、AI Crawl Control、Bot Fight Mode、Under Attack、WAF和缓存规则；这些可在Worker之前拦截。Bot Fight Mode不能用WAF Skip绕过，不应盲目开启来满足本Skill。需要合法爬虫例外时使用支持例外的功能或调整具体冲突规则。豁免依据平台认证或官方最新IP验证，仅限公开读路径，不跳过后台和询盘安全检查。不要把几种UA白名单宣传成支持“所有SEO/GEO”。

## 发布验收（每个网站必须执行）

1. 检查上传范围、完整静态包和 Worker路由，关闭/保护可绕过边缘的原站入口。部署配置生成与本地测试只能记 GENERATED / NOT_RUN；公网验证后才记录启用。
2. 实际域名匿名及禁JS读页面、图片、PDF、robots、sitemap，核对状态、正文、canonical和响应头；查询参数不改变限流身份。更换Googlebot/OAI-SearchBot UA的测试只能证明UA兼容，不能证明平台身份或真实收录。
3. 验证私有路径404、HEAD、未知路径404、非法方法405、防嵌套头。只在隔离预发布环境暂调低额度验证429/Retry-After及恢复，不对客户生产站做压力测试。检测限流异常告警；确认边缘认证的爬虫可取同一公开正文。
4. 同源/外部接收服务分别检查正常提交、错误Origin、超大体、超限、后端离线和真实收件/入库。记录证据链接、时间、部署版本和未测项。上线后观察合法抓取429/403、真实询盘失败率再调额度，不按IP数量推断恶意。
5. GSC实时抓取/收录、Bing及目标AI系统访问/引用分开验收。无权限或无证据写NOT_RUN。机器人规则、版权声明和本地测试不等于线上防护成功。

`private/protection-status.json` 每次构建重置为 runtime NOT_RUN；验收证据与当前部署版本关联，旧PASS不能沿用。

## 官方依据（2026-09-27核验）

- [Workers 静态资产及先执行Worker](https://developers.cloudflare.com/workers/static-assets/binding/)：路径与资源入口配置。
- [原生限流绑定](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)：每位置计数、最终一致性、共享IP局限、监控与命名空间。
- [Request 边缘属性](https://developers.cloudflare.com/workers/runtime-apis/request/)：botManagement字段可用性，不信任自报UA。
- [Bot Fight Mode 限制](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/)：WAF Skip不能绕过该功能。
- [Googlebot 身份验证](https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot)、[OpenAI bots](https://developers.openai.com/api/docs/bots)：身份核验与搜索/训练/用户触发访问分开。
