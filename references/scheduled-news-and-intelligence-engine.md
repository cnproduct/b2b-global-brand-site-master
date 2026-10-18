# Automated 30-Day Scheduled Industry News & Blog Engine Specification
> **RenWork Web Create Skill v4.3.0 Engine Specification**  
> *Deterministic 30-Day Scheduled Intelligence Queue, In-Depth Engineering Content (≥3,000 Words & ≥2 Images), Cloud/Edge Timed Publishing, and Visual Admin Control.*

---

## 1. 业务目标与价值定位 (Value Proposition)

在竞争激烈的全球 B2B 工业与制造业出海赛道中，千篇一律的模板化博客（AI-Slop）不仅无法建立海外大买家采购委员会的信任，更会被 Google 核心算法与 AI 搜索引擎（Perplexity、ChatGPT Search、Gemini AI Overviews）直接降权。

**自动 30 天排期行业前沿智库与深度博客发布引擎** 确立了出海网站“前沿行业话语权”的标准化基础设施：
1. **抢占 6 大高价值决策意图**：B端与C端最新资讯、下一代新材料工程、畅销/新锐款式结构解剖、B端头部平台热词异动、C端爆款转化密码、未来 30/60/90 天排产与出货预测。
2. **硬性深度质检门禁**：
   - **每篇字数严守 ≥ 3,000 字**：严禁泛泛而谈的套话，必须包含真实的材料物理力学参数表、加工工艺对比、权威合规认证测试标准、海外买家避坑指南、装柜成本核算及 RFQ 询盘触发器。
   - **每篇配图严守 ≥ 2 张高清工程/实景图**：包含分子晶体/剖面 CAD 图、跌落/微波/耐压实验室实测图或 40HQ 码垛图，显式标注 `width`、`height` 与描述性 `alt`，彻底消除 CLS 跳动并满足 a11y 无障碍标准。
3. **云端后台与边缘定时发布**：
   - 支持提前 30 天自动化批量或按需生成高品质图文储备底账；
   - 支持在后台可视化调整每日发布时间点；
   - 支持云端自动化发布（Cloudflare Worker 定时路由拦截 / GitHub Actions 每日定点静态构建 / 本地定时守护进程）；
   - 自动联动刷新 `news.html` 列表、`sitemap.xml` 站点地图、以及 `llms.txt` / `llms-full.txt` 权威 AI 检索事实库。

---

## 2. 6 大核心选题支柱矩阵 (The Six Content Pillars)

| 选题支柱 | 采购商核心关切 (JTBD) | 必含工程数据与实证内容 |
| :--- | :--- | :--- |
| **① B端与C端最新行业新闻** | 欧美及目标市场最新行业准入法规、关税变动、消费人群习惯变迁 | 关税编码 HS Code、FDA/LFGB/CE 最新指令、欧美零售商库存周期变化趋势 |
| **② 最新材料工程创新与绿色环保** | 寻找性能更优、更环保或能规避碳税关税（如欧盟 PPWR / CBAM）的新材料 | 密度、拉伸模量、热变形温度 (HDT)、食品级测试报告、生物降解周期、碳减排百分比 |
| **③ 畅销款式与最新款式深度拆解** | 为什么某款产品能在海外大卖？模具设计、分格比例、防漏密封的工程机理 | 模具抽芯滑块设计、双色注塑 (2K/LSR) 胶位图解、10,000次卡扣疲劳测试曲线 |
| **④ B端头部平台动态** | 阿里巴巴国际站、环球资源、Made-in-China、ThomasNet 上的大宗采购异动 | 搜索关键词月度暴增比率、大宗买家询盘属性分布、商超验厂（Disney/Sedex/BSCI）硬性门槛 |
| **⑤ C端大平台热卖爆款转换密码** | 亚马逊 Best Seller、TikTok Shop、Temu、Shein 热卖款的供应链代工适配 | 终端爆款差评痛点分析（如漏汤、卡扣断裂、微波打火）、工厂技术改进方案与私模防侵权策略 |
| **⑥ 预测未来 30/60/90天增长趋势** | 避开海运旺季拥堵、合理安排开模确认与大货生产排期 | 倒推时间线（倒排日历）：第 1-30 天打样开模 → 第 31-60 天大货注塑装箱 → 第 61-90 天海外到港上架 |

---

## 3. 文章内容结构与字数硬门槛标准 (≥3,000 Words Architecture)

每篇新闻/深度博客必须遵循以下 6 幕式长文专业架构，严禁注入无意义重复废话：

```markdown
# [主标题]: [核心技术/趋势突破] + [买家决策收益]
> [副标题/Executive Summary]: 3 行以内的浓缩核心结论，包含关键参数变动与行动建议。

## 1. 行业宏观背景与供需痛点穿透 (Industry Macro & Sourcing Pain Points) [~500 words]
- 阐明为什么当前时间节点该议题至关重要（Why-Now 信号）；
- 传统方案的缺陷（材料老化、测试失效、关税惩罚、消费者退货）。

## 2. 核心技术机理与材料工程数据对照 (Technical Mechanism & Materials Science) [~800 words]
- 深入物理力学与化学特性；
- 插入完整的 **Markdown 多维参数对比表**（例如 304 vs 316 vs 钛合金，或 PP vs Tritan vs PLA）；
- **必配图 1**：材料显微结构/模具 CAD 剖面/测试仪器实测图（带规范 alt, width, height）。

## 3. 供应链全流程可行性与制造工艺控制 (Factory Engineering & Quality Assurance) [~600 words]
- 实际生产车间注塑/冲压/表面处理公差（如 ±0.02mm）；
- 质量控制标准（MIL-STD 跌落、真空负压检漏、盐雾耐腐蚀测试）；
- 核心检测设备（三坐标光学测量仪、液相色谱仪、扭矩拉力机）。

## 4. B端与C端市场数据多维验证 (Market Data & Platform Dynamics) [~500 words]
- 引用 B 端平台（Alibaba/环球资源）与 C 端零售（Amazon/TikTok）的真实搜索或销售指数；
- 分析海外买家商业采购溢价与零售毛利空间（中国出厂价 vs 欧美零售定价对比）；
- **必配图 2**：真实产品应用场景图/40HQ 装柜排布图/全球认证测试报告原件。

## 5. 常见采购陷阱与海外买家风控清单 (Sourcing Pitfalls & Buyer Risk Reversal) [~400 words]
- 避坑指南：识别“回收料掺杂”、“电镀涂层剥落”、“无资质冒充真验厂”等常见猫腻；
- 验货与出货前验收清单 (Pre-Shipment Checklist)。

## 6. 未来 30/60/90 天行动计划与直接询盘 (Sourcing Action Plan & Direct RFQ) [~300 words]
- 具体的排产交期指导（样品 48h、模具 15天、整柜 25天）；
- 触发直接询盘卡片（提供免费材质检测报告、样板寄送或 CAD 图纸下载）。
```

---

## 4. 技术实现架构 (Technical Architecture)

### 4.1 数据仓储层 (`content/scheduled-news/queue.json`)
```json
{
  "version": "1.0",
  "generated_at": "2026-10-09T00:00:00Z",
  "total_scheduled": 30,
  "articles": [
    {
      "id": "post-2026-10-10",
      "slug": "news-2026-back-to-school-bento-trends",
      "publish_date": "2026-10-10T08:00:00Z",
      "category": "B2B & B2C Trends",
      "title": "2026 Back-to-School Global Bento Box Procurement Trends: Safety Norms, Portion Control & Sourcing Timelines",
      "author": "Dr. Keith Vance, Materials & Food Safety Engineering Lead",
      "word_count": 3280,
      "images": [
        {
          "url": "images/products/kids-bento-exploded-view.webp",
          "alt": "5-compartment kids bento box exploded view with silicone seals",
          "width": 1200,
          "height": 800
        },
        {
          "url": "images/products/leakproof-testing-rig.webp",
          "alt": "50kPa negative pressure vacuum leak testing rig for bento lunch boxes",
          "width": 1200,
          "height": 800
        }
      ],
      "status": "scheduled",
      "file_path": "news-2026-back-to-school-bento-trends.html"
    }
  ]
}
```

### 4.2 自动化执行引擎 (`scripts/scheduled_content_engine.py`)
该脚本具备以下核心能力：
1. **`--generate-30days`**：一键生成覆盖未来 30 天的高标准排期文章库，每篇必须通过 `word_count >= 3000` 与 `len(images) >= 2` 的防御性断言；
2. **`--publish`**：定时触发（可由 Cron、GitHub Actions 或 Cloudflare 定时调用），检测 `publish_date <= now` 且 `status == 'scheduled'` 的文章：
   - 自动生成符合 Vercel 12 维规范的高保真独立静态 HTML 页面；
   - 自动更新主新闻聚合页 `news.html` 中的文章卡片与时间轴；
   - 自动在 `sitemap.xml` 中追加 `<url>` 及 `<image:image>` 元数据并配置当前更新时间；
   - 自动在 `llms.txt` 与 `llms-full.txt` 中写入新的索引条目，供给 Perplexity、Claude、ChatGPT 爬虫学习；
   - 标记该文章状态为 `published` 并持久化。
3. **`--audit-queue`**：对文章库执行严格体检，检查字数、图片、Schema 与死链；
4. **`--serve-admin`**：一键拉起基于本地或云端的轻量管理面板。

### 4.3 云端后台可视化管理面板 (`admin/scheduled-manager.html`)
- **30 天日历排期看板**：按天展示待发布文章卡片，状态标签高亮（已发布 Published / 待发布 Scheduled / 草稿 Draft）；
- **字数与配图严格核验徽章**：实时统计文章真实字数（通过绿标提示：`✓ 3,420 Words (Pass ≥3000)`），配图数量（`✓ 2 Images Configured`）；
- **一键即时发布 (Publish Now Override)**：遇到突发行业热点时，允许管理员在后台直接将某篇待发布文章即时发布上架；
- **全屏长文预览抽屉**：无需跳转直接在后台以高保真排版预览 3,000+ 字长文与高清图片。

### 4.4 边缘与云端安全防护 (`templates/edge-worker.mjs`)
在 Cloudflare Workers 或 Vercel Edge 层面配置拦截策略：
- 未到发布日期的文章 URL 严格返回 `404 Not Found`，防止 Googlebot 提前索引未发布的草稿页面；
- 携带管理员认证 Token 时（例如 `?preview_token=xxx`）允许管理员提前免密查看未发布页面；
- 到达发布时刻后，边缘节点自动失效缓存，对外开放无缝访问。

---

## 5. 验收标准与测试清单 (Definition of Done)

所有接入本引擎的网站在交付前必须通过以下验收：
1. [ ] `content/scheduled-news/queue.json` 包含未来 30 天每日 1 篇完整文章记录（共 30 篇）；
2. [ ] 每一篇排期文章经字数统计程序检测，正文字数必须 **≥ 3,000 字**；
3. [ ] 每一篇排期文章至少配置 **≥ 2 张** 具真实产品/技术含义的高清图片，必须包含正确的 `alt`、`width` 和 `height` 属性；
4. [ ] 每一篇排期文章包含完整且合法的 `NewsArticle` 或 `TechArticle` JSON-LD Schema；
5. [ ] 后台管理面板 `admin/scheduled-manager.html` 可正常访问并交互，具备状态筛选、改期与预览功能；
6. [ ] 运行 `scripts/scheduled_content_engine.py --audit-queue` 结果为 0 报错；
7. [ ] 全站通过 `layout_typography_auditor.py` 自动化体检（0 阻断性错误）。
