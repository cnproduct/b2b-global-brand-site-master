# 02. 外贸出口企业知识库 21 模块映射与事实中台规范 (Export KB 21-Module Matrix)

本规范深度继承 **`cnproduct/renwork-export-kb-suite`（外贸出口企业 AI 知识库标准框架 V3.0/V4.0）** 的精髓，确立“事实先于生成、证据强于承诺”的建站知识底座。

---

## 一、21 模块跨端数据流与独立站映射表

当企业仅提供 50–100 字简要介绍与 Logo 时，系统通过**行业适配器（Industry Profiles）**与**确定性外推规则**，自动化将知识骨架装配至独立站各技术板块，彻底杜绝虚假套话：

| 模块编号 | 模块名称 | 事实数据核心字段 | 独立站直连呈现板块 | 默认置信度状态 |
|:---|:---|:---|:---|:---:|
| `00_kb_governance` | 知识中台总索引与治理 | 版本号、成熟度评分 (K0–K4)、三批缺口队列 | 业务速查卡 (Cheat Sheet)、建站审计报告 | 已验证事实 |
| `01_sources_permissions` | 证据源与贸易术语词典 | Incoterms 2020、HS 编码矩阵、多语言同义词 | 行业专业词汇库、URL 语义锚点 | 已验证事实 |
| `02_company_identity` | 企业法律身份与硬实力 | 工厂面积 (㎡)、员工数、自动化产线数、经纬度坐标 | 关于工厂（`about_factory.html`）、Schema `LocalBusiness` | 公开事实 |
| `03_brand_messaging` | 品牌口径与对外话术 | 核心价值主张 (UVP)、30/100/300 字口径、禁用词表 | 首页 Hero 主标与副标、`<meta description>` | 建议策略 |
| `04_product_catalog` | 产品独立卡与参数图谱 | 主推型号、公英双制式尺寸/公差、材质物性 | 产品目录（`products_catalog.html`）、Schema `Product` | 公开事实 / AI推断 |
| `05_manufacturing_quality` | 智造工艺、质检与 AQL | 8 道工序质检流、AQL 0.65/1.5/4.0、实验室设备 | 智造品质页（`capabilities.html`）、检验节点看板 | 公开事实 |
| `06_certification_compliance` | 认证法规与准入矩阵 | 证书编号、颁发机构、标准代号 (ASTM/CE/FDA/ISO) | 认证台账页（`certifications.html`）、Schema `TechArticle` | 已验证 / 待确认 |
| `07_commercial_delivery` | 商务条款、交付与防欺诈 | MOQ 梯度、加急交期、收款账号多渠道防篡改声明 | 阶梯报价卡、安全交易声明、Google Merchant 政策 | 待企业确认 |
| `08_market_intelligence` | 目标市场偏好与季节节奏 | 北美/欧洲/中东差异化要求、采购周期日历 | 行业解决方案导航、公英双制式自动适配 | 建议策略 |
| `09_icp_buyer_personas` | ICP 与决策委员会痛点 | 设计师/工程承包商/品牌商/批发商 4 轨角色需求 | 首页按买家角色导流器 (Buyer Archetype Router) | 建议策略 |
| `10_buyer_intent_signals` | 买家寻源意图触发器 | 样品索样、大货询价、图纸定制、急单交付 | 场景化高转化 CTA（"Instant CAD/BIM Download"） | 建议策略 |
| `11_competitors_differentiation` | 竞品差异与证据链 | 痛点—能力—实测实物证据对照表 | Bento 看板：Why Choose Us vs Traditional Factories | 建议策略 |
| `12_product_market_fit` | 产品—国家—买家匹配 | 区域标准适用性（美标 UL/ASTM vs 欧标 CE/EN） | 动态市场合规徽章（US/EU/Middle East Ready） | 建议策略 |
| `13_lead_discovery` | 线索验真与客户背调 | 买家资质审核准则、虚假询盘过滤器 | RFQ 智能询盘表单预审字段 | 规则与流程 |
| `14_customer_asset_lifecycle` | 客户生命周期与分层 | 8 类实体关系、S/A/B/C/D 分层、复购预警 | 客户专属订购通道（VIP Reorder Portal） | 数据驱动 |
| `15_inquiry_qualification` | 询盘资格识别与推进 | 询盘 10 步速检、L1/L2/L3 三层下钻问题清单 | 智能 RFQ 表单提示语（提示买家提交完整参数） | 规则与流程 |
| `16_solution_quotation` | 方案阶梯报价与选型 | **Good / Better / Best** 阶梯配置表、定制深度 (L1–L4) | 深度代工页（`oem_odm_customization.html`）阶梯卡 | 模板与标准 |
| `17_objection_negotiation` | 异议抗辩与谈判红线 | 10 类高频异议（价格贵/交期紧/MOQ高）权威对答 | 交互式技术与采购 FAQ 问答库（Schema `FAQPage`） | 话术与红线 |
| `18_sales_content_templates` | 全渠道销售物料与邮件 | 样品盒说明书、TDS 技术数据单、产品彩页 PDF | 资料中心一键索取（"Download 2026 Technical Dossier"） | 模板库 |
| `19_order_delivery_aftersales` | 订单跟踪与 P1–P3 售后 | 生产进度可视、出货前大货样、P1/P2/P3 售后响应 SLA | 售后保障承诺条约与无忧退换政策 | SOP与标准 |
| `20_learning_metrics` | 业务复盘与持续学习 | 沉默原因诊断、成败复盘模板、知识库迭代版本 | 网站持续更新日志与版本迭代说明 | 持续优化 |

---

## 二、六态置信度体系与防虚构红线 (Truth Guardianship)

系统严禁将未经企业确认的假设伪装成不可辩驳的客观事实：
1. **已验证事实 (Verified Fact)**：有企业提供的营业执照、检验报告、实地勘验照片为证；
2. **公开事实 (Public Fact)**：由企业公开官网、海关报关记录、第三方公信名册收录；
3. **AI 推断 (AI Inference)**：基于行业基准模板推演的参数（例如：鞋厂 2 条成型线推算日产能约 3,000–5,000 双），生成时明确标注为推断值；
4. **建议策略 (Suggested Strategy)**：为企业出海规划的差异化定位与营销话术；
5. **待补充 (To Be Added)**：关键缺口（如：具体银行开户行、实验室具体仪器型号）；
6. **已失效 (Deprecated)**：过期的历史认证或停产旧型号。

---

## 三、Good / Better / Best 三阶报价方案模型

在 `oem_odm_customization.html` 中呈现的阶梯方案矩阵，有效降低买家决策门槛：

```
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│       Tier 1: GOOD      │     Tier 2: BETTER      │      Tier 3: BEST       │
│      (经济引流/标品)     │       (主推/差异化)     │      (高端旗舰/定制)     │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ • 行业标准基础物性       │ • 增强型高物性/长寿命    │ • 军工/严苛环境特种物性  │
│ • 标准公装包装          │ • 环保 FSC 彩盒定制     │ • 奢华全套礼盒+防伪微标 │
│ • MOQ: 500 pcs          │ • MOQ: 1,000 pcs        │ • MOQ: 3,000 pcs        │
│ • 交期: 15–20 天        │ • 交期: 20–25 天        │ • 交期: 30–35 天        │
│ • 适合: 批发流通渠道    │ • 适合: 主流品牌商商超   │ • 适合: 行业高端项目定制 │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

---

## 四、三批缺口确认队列执行协议 (Missing Data Queues)

系统在初次建库后，绝不一次性向企业抛出冗长问卷，而是按优先级分为三批：
- **第 1 批（上线阻断项 - 24小时内）**：核准公司注册全称（英文）、核心主推 3 款产品与型号、联系人官方可信邮箱与 WhatsApp；
- **第 2 批（转化加速项 - 3天内）**：核准标准 MOQ、加急交期天数、样品寄送与打样退费政策、现有持证报告证书编号；
- **第 3 批（风控与规模项 - 7天内）**：核准指定海运港口（如厦门港/宁波港/深圳盐田）、正式外汇电汇银行账号及多渠道核验防篡改声明。
