# B2B 建站 Skill：SEO / GEO 官方事实核验

核验日：2026-09-27。仅将运营商官方文档、公告和提案原文作为规范依据；以下为简述与实施建议，不是原文摘录。未操作任何公司 Search Console / Bing 后台；文档存在功能不等于目标账号已出现数据。

| 主题 | 已确认结论与时效 / 冲突 | 融合 Skill 应如何处理 | 官方原始来源 |
|---|---|---|---|
| Google AI 搜索基本要求 | 新 AI 优化指南最后更新 2026-07-10：基础 SEO、有用且独特的一手内容、可抓取/索引/显示摘要仍是核心。没有特别的 AI Schema、固定字数、强制切块；批量覆盖所有 fan-out 变体可能落入规模化内容滥用。 | 把工厂真实技术经验、验证过的规格与选型证据放在主线；删除关键词密度、固定 40–60 词、固定每段长度、批量“问题×国家”页面等硬性规则。 | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide |
| Google 官方新旧文档差异 | 旧 `ai-features` 页面最后更新 2025-12-10，只谈 AI 流量并入 Web 性能报告；2026-06-03 公告及新帮助页已推出单独生成式 AI 报告，且仍计入整体报告。两条可以共存，不能用旧页推出“没有独立 AI 报告”。 | 冲突登记：优先采用具体功能的新帮助页及带日期公告。新旧 URL 都保留来源，不以旧知识覆盖新文档。 | https://developers.google.com/search/docs/appearance/ai-features ; https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports |
| GSC 生成式 AI 报告 | 帮助页明确 2026-08-31 全球推出；Search 报告覆盖 AI Overviews / AI Mode 的展示量，可按页面、国家、日期、设备查看。报告页仍残留“rolling out over time”说明；数据不足也可能不显示报告。未见该页提供独立 AI 点击、CTR、查询词。 | 先实测账号报告和实际字段；没有入口时记 unavailable，不当作 0；保留整体 Web 报告、分析工具引荐和询盘数据。不能将整体 Web 点击冠以 AI 点击。导出 ~ / - 变零需保留原始缺失状态。 | https://support.google.com/webmasters/answer/16984139 |
| GSC 生成式 AI 控制 | 官方写 2026-08-31 全球推出。Settings > Search generative AI 可包含/排除链接与内容；父子属性可能继承。该控制独立于模型训练，也不改变其他搜索部分的排名或纳入。 | 在上线检查中读取目标属性有效值和继承来源，记录 include / exclude / unavailable；不要假设需要新建一个 opt-in，也不要未经站主意愿修改原有排除策略。训练、索引、搜索生成式展示应分别记录。 | https://support.google.com/webmasters/answer/16908024 |
| FAQ 富媒体结果 | Google 更新日志 2026-05-08 声明自 2026-05-07 起不再展示 FAQ rich result；6 月移除该功能文档。 | FAQ 留作真实采购答疑；删去“通过 FAQPage 获得 Google FAQ 富媒体”的承诺。FAQPage 语义词汇存在不等于 Google 当前支持该富媒体。 | https://developers.google.com/search/updates |
| Bing AI Performance | 2026-02-10 公开预览覆盖 Copilot、Bing AI 摘要及部分合作体验；衡量引用次数、被引页面、grounding 查询和趋势。汇总/样本不能解释成排名或每次提问的完整日志。 | 增设 Bing Webmaster Tools 验证与报告基线；与 Google impressions、站内 referral、询盘分开。相同时间窗观察，不做跨平台指标相加。 | https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/ |
| Bing 6 月扩展 | 2026-06-16 新增全球预览 Intents、Topics、Citation Share、Compare。Citation Share 是某 grounding 查询全部引文中归属站点的比例，不是流量份额/权威得分，也不公开竞品域名。 | 按账号实际字段选用这四项，记录 preview 和采样；禁止报告“统一 GEO 排名”。内容变化与引用变化只是观察关联，不能自动归因。 | https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/ |
| OpenAI 爬虫 | OAI-SearchBot 用于 ChatGPT 搜索；GPTBot 是模型训练控制，两者独立。ChatGPT-User 是用户触发访问，不负责决定搜索纳入，robots 可能不适用。 | 建立 search / training / user-fetch 三栏，禁止把“开放 GPTBot”设为搜索必需。除 robots 还检查 CDN/WAF，并按官方 IP 验证真实日志；模拟 UA 成功不等于官方爬虫成功。 | https://developers.openai.com/api/docs/bots |
| Perplexity 爬虫 | PerplexityBot 用于搜索展示，文档声明不是基础模型训练抓取；Perplexity-User 为用户触发，通常不理会 robots。官方 WAF 指引同时匹配 UA 与当前 IP。 | 用户触发抓取单独列示；只维护官方 IP 来源，不硬编码永不过期的范围；禁止仅靠 UA 白名单放行。 | https://docs.perplexity.ai/docs/resources/perplexity-crawlers |
| llms.txt 当前提案 | 原始提案现为 v2，修改日期 2026-08-10：可按路径提供 llms.txt、链接干净 Markdown，并以 alternate / describedby 关系发现。仍是提案。 | 可选生成公共、已批准的内容导航；优先链接权威页面或同步 Markdown；不得公开内部联系人、客户/成本/报价等 KB 内容；不当 SEO 发布闸门。 | https://llmstxt.org/ |
| llms.txt 与 Google / Lighthouse | Google 搜索新指南说 Google Search 不用该文件作为特殊输入或排名手段。Chrome Lighthouse 2026-05-05 文档明确文件可选，404 为 N/A，获取时服务器错误才触发该项问题。两者服务不同目标，并不冲突。 | 删除“无 llms.txt = GEO 不合格”。选择维护时验证链接、权限、与 HTML 同步。报告将 Agent 可用性和搜索表现分开。 | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide ; https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt |
| WebMCP 最新状态 | 不应只停在 2026-02 early preview；2026-06-09 Chrome 149 origin trial，2026-09-03 W3C 社群会议仍说明 Chrome/Edge trial，并已出现 ChatGPT Desktop、Brave 实现。 | 可选试验模块：只在产品有代理选型/表单操作场景时启用。优先可访问 HTML 和正常表单；不当索引/排名条件；实际开发时重新核验 API、浏览器支持、权限及人类确认边界。 | https://developer.chrome.com/blog/ai-webmcp-origin-trial ; https://www.w3.org/2026/09/03-webmachinelearning-minutes.html ; https://developer.chrome.com/docs/ai/webmcp |

## 建议作为一套统一验收口径

- **发布前可验证**：事实/素材权限、渲染与链接、canonical/hreflang/robots/sitemap、适用结构化数据与可见内容一致、页面体验、表单实际收件。
- **发布后单独验收**：抓取 → 收录 → 搜索展示 → 生成式展示/引用 → 来访 → 有效询盘；前一项不证明后一项。
- **观测可复现**：平台、账号/地区/语言、日期、原始查询/提示、页面/引用 URL、证据截屏或导出、样本范围与缺失值。模拟提示抽样不得称为全网份额。
- **规范可更新**：每次项目启动/发布前复核动态官方来源，登记 checked_at、source_published_at、claim、scope、status（confirmed / preview / proposal / disputed / unavailable）；不要承诺永久“最新”。
