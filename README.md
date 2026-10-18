# B2B Global Brand Site Master · V3.0 全链路大一统旗舰版

从前置跨境爆品情报、全球标杆解构、公司 Logo 与简介，持续构建外贸 B2B 品牌、企业知识库、数字资产、30 天排期行业智库与世界级行业独立站；同时内置通用 Skill 七步机制蒸馏能力。

V3.0 将 **`b2b-global-brand-site-master`**、**`renwork-web-create-skill` (v4.3)** 与 **`b2b-limestone-geo-site-builder`** 全面融合为统一入口：

**三轨智能路由 (Mode A 原创 / Mode B 1:1 复刻 / Mode C Skill 蒸馏) · 8 大构建阶段 SOP · 跨境产品情报 DVI 引擎 · Anthropic 反 AI-Slop 两轮设计 · Vercel 12 维界面体检 · 22 类行业蓝图 · 21 模块事实底座 · 双模集装箱装柜算力 · GEO 五层端点 (`/llms-full.txt` & `/ai/*.json`) · 30 天排期智库发布引擎 (≥3,000字/≥2图) · 默认边缘防护。**

---

## 🏛️ 三轨路由与 8 大构建阶段 SOP

### 1. 三轨智能路由 (Triple-Track Workflow)
- **Mode A（默认：买家洞察原创增长与 8 阶段 SOP）**：前置跨境产品情报穿透 $\rightarrow$ 买家委员会 4 角色 JTBD 与官方关税洞察 $\rightarrow$ 三互补标杆机制蒸馏与文化双轨重命名 $\rightarrow$ Anthropic 反 AI-Slop 两轮设计 $\rightarrow$ 双模海运装柜算力 $\rightarrow$ 同源事实编译与 Clean URLs $\rightarrow$ GEO 五层端点 $\rightarrow$ 30 天排期行业智库长文引擎 $\rightarrow$ Vercel 12 维体检与默认边缘防护。
- **Mode B（1:1 严格证据复刻与文化重塑分支）**：当明确要求“1:1 复刻/克隆某站”时，启动 `site_forensics.py` 探针取证、CSS Token 提取、文化双轨重命名脱敏、像素级契约还原、图实一致性核查（$\Delta E < 5$）及零视觉变动注入 GEO 五层端点。
- **Mode C（通用 Skill 七步机制蒸馏工作流）**：当输入包含“优化这个 Skill：〈路径/仓库〉”时，执行两层能力缺口诊断（通用 vs 领域，不向非网站类 Skill 强加 SEO/关税规则）、GitHub/Hugging Face 资源甄别、六步机制蒸馏链、代码改造、三态经验验证与 `SKILL_OPTIMIZATION.md` 报告交付。

### 2. 全行业 8+1 构建阶段全景表

| 阶段 | 阶段名称 | 核心交付与执行机制 |
|---|---|---|
| **阶段零** | **跨境爆品情报穿透 & 全球三大巨头标杆排查** | 穿透 TikTok/Amazon/Google Trends/海关提单 5 大信号源测算 DVI 爆款；锁定细分赛道**三大巨头**（① 技术规范与 GEO 权威、② 高端视觉溢价天花板、③ 场景长尾词之王） |
| **阶段一** | **买家委员会 4 角色 JTBD、关税洞察与品牌基因** | 拆解使用者/技术评估/商业决策/财务物流 4 角色弹药；核验 WTO/EU/USITC 关税与季节窗口；锚定中国产业带坐标与真实产能（三层数据隔离） |
| **阶段二** | **机制蒸馏、文化双轨重命名与图实一致铁律** | 对照学习与反事实去冗余；建立 `[文化主名] [工艺/功能] [品类词]` 双轨命名剥离 Trademark；微距实拍与场景图色差 $\Delta E < 5$ |
| **阶段三** | **Anthropic 反 AI-Slop 两轮设计 & 工程标准锚定** | 四大强制约束 + Pass 1/Pass 2 反模板化审视（大胆用在一处，克制留给全局）；全站绑定 ASTM/CE/FDA/ISO/ГОСТ 实测指标 |
| **阶段四** | **海运双模集装箱装柜测算引擎 & 采购组件** | `design_math.py` 提供**外箱体积/毛重模式 (`container`)** 与**重货限重硬瓶颈模式 (`stone-container`，20GP 限重 26.5 吨)** |
| **阶段五** | **同源事实静态编译、Clean URLs 与 Anti-FOUC** | 核准事实卡同源生成 HTML/Schema/Sitemap；全面剥离 `.html` 后缀；CSS 内容哈希 `?v={hash}` 与隐藏抽屉内联隔离 |
| **阶段六** | **2026 全球 AI Bot 吸流量 GEO 五层矩阵** | `llms: true` 发布构建时自动产出 `/llms.txt`、`/llms-full.txt` 及 `/ai/summary.json`、`/ai/products.json`、`/ai/faq.json`、`/ai/vendor-comparison.json` |
| **阶段七** | **30 天排期行业智库长文引擎 & 第一方三段式 RFQ** | `scheduled_content_engine.py` 管理 30 天排期队列（每篇 ≥3,000 字、≥2 张高清工程图）；Cloudflare Worker + Turnstile 验签三段式询盘闭环 |
| **阶段八** | **Vercel 12 维界面体检、边缘防护与 6 大防错军规** | `layout_typography_auditor.py --strict` 自动化 `file:line` 审计；Cloudflare Workers 默认防护包；[6 大防错军规](references/failure-cases-and-guardrails.md) 与 CIS/Yandex 扩展 |

---

## 快速开始与核心工具链

将本仓库安装到 Agent 的 skills 目录（如 `~/.gemini/config/skills/b2b-global-brand-site-master/` 或 `~/.codex/skills/b2b-global-brand-site-master/`），以 [SKILL.md](SKILL.md) 为入口。

```bash
# 1. 查看全部 22 个行业蓝图并初始化项目
python3 scripts/sitekit.py industries
python3 scripts/orchestrator.py --name "Example Company" \
  --intro "We quarry and process architectural limestone pavers." \
  --industry limestone --out /tmp/example-company-project

# 2. 编译草稿与发布候选 (release 模式下若 llms=true 自动生成 /llms-full.txt 与 /ai/*.json)
python3 scripts/orchestrator.py --project /tmp/example-company-project
python3 scripts/orchestrator.py --project /tmp/example-company-project --release

# 3. 运行站点完整性审计 + Vercel 12 维 UI/UX 与 Clean URLs 严格体检
python3 scripts/validate_site.py /path/site-output --release --domain https://example.com
python3 scripts/layout_typography_auditor.py --strict /path/site-output

# 4. 设计数学、安全 URL 拼接与双模集装箱装柜算力
python3 scripts/design_math.py contrast '#334155' '#ffffff'
python3 scripts/design_math.py fluid 36 64 360 1440
python3 scripts/design_math.py safe-url https://example.com stone-flooring/limestone
python3 scripts/design_math.py container --length 540 --width 380 --height 420 --weight 14.5 --pcs 24
python3 scripts/design_math.py stone-container --area 480 --thickness 20 --density 2620

# 5. 30 天排期行业智库长文引擎 (≥3,000字 & ≥2图/篇) 与单页取证探针
python3 scripts/scheduled_content_engine.py --self-test
python3 scripts/scheduled_content_engine.py --audit-queue
python3 scripts/site_forensics.py https://example.com /tmp/evidence-capture
```

---

## 22 类行业采购蓝图

完整字段见 [assets/industries.json](assets/industries.json)：

| 行业 ID | 范围 | 采购路径 |
|---|---|---|
| `machinery` | 工业机械与自动化 | 工况→机型→系统配套→验收→服务 |
| `components` | 五金与精密零部件 | 图纸→材料→公差→工艺→批量 |
| `building-materials` | 建材与装饰材料 | 应用→材质→性能→安装→样板 |
| `limestone` | 天然石灰石与建筑景观石材 | 空间场景→表面防滑工艺→ASTM/CE/ГОСТ力学参数→文化双轨选色→重货20GP配载与寄样 |
| `bento` | 便当盒与餐厨餐饮容器 | 品类→分格材质→防漏/微波认证→OEM定制→装柜交期 |
| `sanitaryware` | 卫浴洁具与水暖 | 类型→尺寸接口→表面→市场条件→样品 |
| `hygiene` | 吸收性卫生用品与湿巾 | 使用场景→尺码规格→材料结构→包装→贴牌 |
| `footwear` | 鞋类制造与出口 | 用途→鞋楦尺码→材料结构→打样→测试 |
| `apparel` | 服装纺织与运动服 | 用途→面料→版型→工艺→样衣→尺码 |
| `bags` | 箱包与户外包 | 场景→容量结构→材料五金→测试→定制 |
| `furniture` | 家具家居与工程配套 | 空间→尺寸→材料饰面→结构→装配运输 |
| `packaging` | 包装与印刷 | 结构→材料→工艺→版面→样品→批量 |
| `electronics` | 电子元件与电子产品 | 功能→参数→封装/接口→设计资料→供货 |
| `automotive` | 汽车零部件 | 车型/图号→适配→规格→测试→批次 |
| `energy` | 能源电气与照明 | 场景→系统边界→工况→配置→安装服务 |
| `food` | 食品饮料与农产品 | 品类→成分规格→储运→批次→市场 |
| `chemicals` | 化工原料与涂料 | 用途→等级→性能→文件→安全储运 |
| `medical` | 医疗器械与耗材 | 预期用途→型号→技术规格→文件→市场适用 |
| `beauty` | 美妆与个人护理 | 产品概念→配方范围→包材→测试→标签 |
| `toys-sports` | 玩具与运动器材 | 使用者场景→结构材料→安全→包装→定制 |
| `appliances` | 家用电器与商用厨电 | 用途→容量→电气条件→安装→维护 |
| `pet-products` | 宠物用品与宠物食品 | 动物与用途→尺寸/配料→材料/储存→安全→包装 |

---

## 验证和维护

```bash
python3 tests/check_pipeline.py
python3 tests/check_validator.py
python3 tests/check_record_learning.py
node tests/check_estimator.mjs
node tests/check_inquiry.mjs
node tests/check_protection.mjs
python3 scripts/design_math.py self-test
python3 scripts/scheduled_content_engine.py --self-test
```

[MIT License](LICENSE) · [第三方许可](THIRD_PARTY_NOTICES.md)。
