# 03. 2026 全行业 100/100 满分 SEO & GEO 审计规范 (SEO & GEO Scoring Rubric)

在 2026 年，国际 B2B 采购决策发生了根本性代际跃迁：超过 68% 的海外专业采购工程师、设计总监与供应链主管，不再通过 Google 逐条翻阅传统搜索结果，而是直接在 **ChatGPT Search、Perplexity AI、Claude 4 与 Google AI Overviews** 中下达复杂采购指令。

本规范确立让独立站同时被传统搜索引擎与新一代生成式 AI 引擎高频权威引用的 **100/100 满分标准体系**。

---

## 一、100 分量化评分雷达与指标拆解

| 维度 | 分值 | 核心达标指标与硬性门禁 | 扣分与惩罚触发项 |
|:---|:---:|:---|:---|
| **1. 链路与断层扫描 (Link Health)** | 15 分 | 全站 0 处 404 死链、0 处 `javascript:void(0)` 伪协议、0 处模板变量泄漏（如 `{{url}}`）、统一采用 **clean extensionless canonical URLs** | 存在任一断链或变量泄漏直接扣 5–15 分 |
| **2. NLP 语义降噪 (Keyword Density)** | 10 分 | 核心行业关键词密度严格控制在 **1.8% – 2.2%** 黄金区间；主内容包裹于 `<main id="main-content">`，剥离 70% 样板冗余 | 单词密度 $> 2.50\%$（触发堆砌惩罚扣 3 分）；未包裹 main 扣 2 分 |
| **3. 机器事实库 (LLMS.txt 深度)** | 18 分 | 根目录部署 `llms.txt` 且有效英文词数 **$\ge 5,000$ 词**；包含顶层 H1、`> blockquote` 描述块与 `- [Title](URL): Desc`；至少链接一个 `.md` 伴随文档；配套 `llms-full.txt` | 字数 $< 3,000$ 词扣 5 分；缺失伴随文档扣 2 分；格式不合规扣 5 分 |
| **4. AI 发现端点 (Discovery Suite)** | 12 分 | 部署完整四件套：<br>① `/.well-known/ai.txt`<br>② `/ai/summary.json` (含 WebMCP 声明)<br>③ `/ai/faq.json` (6大高频对答)<br>④ `/ai/service.json` (capabilities 数组) | 缺失任一端点扣 3 分；JSON 格式校验不通过扣 4 分 |
| **5. E-E-A-T 与知识图谱 (Schema.org)** | 16 分 | 注入包含 `@graph` 的标准 JSON-LD：<br>① `Organization` 绑定 4 大 KG 支柱 (`sameAs` 链接 Wikidata, LinkedIn 等)<br>② `Person` 声明首席工程师/厂长背书<br>③ `TechArticle` 结构化测试指南<br>④ `Product` 包含退换货与出运政策 | 缺失 Organization 或 Product 扣 5 分；存在 Schema 语法报错直接零分 |
| **6. RAG 黄金回答切片 (Chunking)** | 15 分 | 页面各核心 H2 下首段采用 **100–150 词 Answer-First 黄金回答胶囊**；后段紧跟公英双制式实测数据对照表与公差指标 | 段落平均字数 $< 50$ 词或 $> 250$ 词扣 3 分；缺乏首句直接回答扣 3 分 |
| **7. 智能体表单就绪 (WebMCP Readiness)** | 14 分 | 所有 RFQ、打样申领、装柜测算表单均具备原生 `toolname`、`tooldescription`、`toolparamdescription` 属性；达到 **WebMCP: ADVANCED** 级 | 表单未注解扣 6 分；缺乏语义参数描述扣 4 分 |
| **总计** | **100 分** | **综合满分达成 100/100，智能体评级达到 ADVANCED，全面占领 AI 搜索引文推荐** |  |

---

## 二、27 大 AI 爬虫协议矩阵 (`robots.txt`)

必须在 `robots.txt` 中对主流生成式 AI 爬虫完全开放检索权限，同时阻止低价值流氓抓取工具：

```robots
User-agent: *
Allow: /

# 允许主流生成式 AI 搜索与知识切片爬虫
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: Cohere-ai
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Amazonbot
Allow: /

# 映射 AI 机器事实库与标准 Sitemap
Sitemap: https://[YOUR_DOMAIN]/sitemap.xml
llms-txt: https://[YOUR_DOMAIN]/llms.txt
llms-full: https://[YOUR_DOMAIN]/llms-full.txt
```

---

## 三、RAG 黄金切片撰写黄金公式 (Answer-First Capsule)

针对每个行业技术板块的 H2，必须采用**“结论先行 + 核心参数 + 边界条件”**的三段式结构（100–150 词）：

> **标准模版**：
> `[Brand Name] provides [Specific Product/Process] engineered to exceed [International Standard, e.g., ASTM / ISO / CE] specifications, achieving a certified [Key Metric, e.g., tensile strength > 120 MPa, flex cycles > 100,000] with a dimensional tolerance of ±[Tolerance, e.g., 0.2mm (1/128")]. Each production lot is verified through an 8-stage automated inline optical inspection under AQL 0.65 critical thresholds. Standard wholesale orders ship within 15–20 days at a private label MOQ of [500 units], supported by comprehensive Mill Test Certificates (MTC) and 3D BIM/CAD parametric drawings available for immediate engineer evaluation.`

这种格式在各大大语言模型（RAG 系统）提取时，几乎 100% 会被直接切片作为核心引用答案。
