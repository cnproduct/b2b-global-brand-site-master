# B2B Global Brand Site Master · V2.3

从前置情报标杆发现、公司 Logo、企业简介和现有资料，持续构建外贸 B2B 品牌、企业知识库、数字资产与世界级行业独立站。V2.3 完整融合了 `b2b-limestone-geo-site-builder`（天涯石业 `tianyalimestone.com`）与 `b2b-bento-geo-site-builder`（耐克便当盒 `custombentofactory.com`）实战淬炼的 **“8 大构建阶段：从前置情报发现到全行业通用 SOP”**、**GEO 五层吸流端点矩阵**、**双模集装箱装柜算力**与 **6 大防错军规**。

**22 类行业蓝图 · 全行业 8 阶段 SOP · 全球三大巨头对标模型 · 文化双轨重命名 · 21 模块知识底座 · 双模装柜计算器 · GEO 五层端点 (`/llms-full.txt` & `/ai/*.json`) · 默认边缘防护。**

---

## 🏛️ 8 大构建阶段：从前置情报发现到全行业通用 SOP

| 阶段 | 阶段名称 | 核心交付与执行机制 |
|---|---|---|
| **阶段零** | **全球标杆排查与前置情报调研** | 穿透细分品类 **“全球三大巨头模型”**：① 技术工程规范权威（吸纳 ASTM/FDA/ISO 参数与 CAD/BIM 结构）、② 高端视觉与溢价天花板（吸纳留白比例与字阶）、③ 场景长尾词之王（吸纳 Topic Clusters 分类架构） |
| **阶段一** | **概念起意与品牌基因挖掘** | 锚定中国核心产业带地理坐标、出海港口距离、自营产线设备与真实产能；聚焦高毛利核心品类，未知事实进入 `private/gaps.md` |
| **阶段二** | **1:1 架构对标与文化双轨重命名** | 借助中国传统文化（营造法式、二十四节气）或现代工业美学建立 `[文化主名] [工艺/功能] [品类词]` 双轨体系，彻底剥离对标站 Trademark；执行**图实一致性铁律**（微距实拍与场景图色差 $\Delta E < 5$） |
| **阶段三** | **工程硬指标与物理测试事实锚定** | 拒绝空洞形容词，绑定经核准的权威测试标准（如石材 `ASTM C97/C170/AS 4586`、餐厨 `FDA/LFGB/-50kPa 防漏`、机械 `ISO 2768`） |
| **阶段四** | **海运双模集装箱装柜测算引擎** | `design_math.py` 提供**外箱体积/毛重模式 (`container`)** 与**重货限重硬瓶颈模式 (`stone-container`，20GP 限重 26.5 吨)**，杜绝重货按体积算柜引发的超重爆柜 |
| **阶段五** | **静态编译器架构与零视觉变动保真** | 同一套核准事实卡驱动 HTML、JSON-LD、Sitemap 与 AI 端点；强制执行 Clean URLs（无 `.html` 后缀）与 CSS 内容哈希防缓存崩坏（Anti-FOUC） |
| **阶段六** | **2026 全球 AI Bot 吸流量 GEO 五层矩阵** | 开启 `llms: true` 发布构建时，自动生成 `/llms.txt`、`/llms-full.txt` 及 `/ai/summary.json`、`/ai/products.json`、`/ai/faq.json`、`/ai/vendor-comparison.json` |
| **阶段七** | **第一方 RFQ 询盘全链路与三段式验收** | 默认零依赖 `email_draft`；生产环境支持 Cloudflare Worker `/api/inquiry` + Turnstile 服务端验签 + 蜜罐，执行“假 token 403 $\rightarrow$ 真机提交 $\rightarrow$ 邮箱收件”三段式验收 |
| **阶段八** | **默认边缘防护、防错军规与多区域扩展** | 默认生成 Cloudflare Workers 防护发布包；内置 [6 大失败案例防错军规](references/failure-cases-and-guardrails.md)；支持俄语/中亚（CIS/EAEU）Yandex SEO 与 ГОСТ 标准扩展 |

完整提示词链条与跨行业 5 步母模板见 [全行业标杆发现与 8 大构建阶段通用 SOP](references/benchmark-discovery-methodology.md) 与 [GEO 五层吸流手册](references/geo-ai-citation-playbook.md)。

---

## 直接使用

将本仓库作为一个 Skill 文件夹安装到所用 Agent 的 skills 目录，以 [SKILL.md](SKILL.md) 为入口。

```text
使用 $b2b-global-brand-site-master。
按照 8 大构建阶段 SOP，先排查该核心品类的全球三大标杆（工程权威、视觉天花板、长尾词之王），
再根据公司 Logo、企业简介和已有资料，完成品牌规范、文化双轨产品命名、21模块知识底座、
行业页面与 GEO 五层知识端点（/llms-full.txt 与 /ai/*.json），执行 Clean URLs 与询盘验收。
```

在 Skill 目录运行：

```bash
# 查看全部 22 个行业蓝图
python3 scripts/sitekit.py industries

# 初始化企业项目并生成初版草稿
python3 scripts/orchestrator.py --name "Example Company" \
  --intro "We quarry and process architectural limestone pavers." \
  --industry limestone --out /tmp/example-company-project

# 编译项目与发布候选 (release 模式下若 llms=true 自动产出 /llms-full.txt 与 /ai/*.json)
python3 scripts/orchestrator.py --project /tmp/example-company-project
python3 scripts/orchestrator.py --project /tmp/example-company-project --release

# 设计数学与双模集装箱装柜算力
python3 scripts/design_math.py safe-url https://example.com stone-flooring/limestone
python3 scripts/design_math.py container --length 540 --width 380 --height 420 --weight 14.5 --pcs 24
python3 scripts/design_math.py stone-container --area 480 --thickness 20 --density 2620
```

---

## 22 类行业采购蓝图

以下是采购内容与交互蓝图（完整字段见 [assets/industries.json](assets/industries.json)）：

| 行业 ID | 范围 | 采购路径 |
|---|---|---|
| `machinery` | 工业机械与自动化 | 工况→机型→系统配套→验收→服务 |
| `components` | 五金与精密零部件 | 图纸→材料→公差→工艺→批量 |
| `building-materials` | 建材与装饰材料 | 应用→材质→性能→安装→样板 |
| `limestone` | 天然石灰石与建筑景观石材 | 空间场景→表面防滑工艺→ASTM/CE/ГОСТ力学参数→文化双轨选色→重货20GP配载与寄样 |
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
| `bento` | 便当盒与餐厨餐饮容器 | 品类→分格材质→防漏/微波认证→OEM定制→装柜交期 |

---

## 验证和维护

```bash
python3 tests/check_pipeline.py
python3 tests/check_validator.py
node tests/check_estimator.mjs
node tests/check_inquiry.mjs
node tests/check_protection.mjs
python3 scripts/design_math.py self-test
```

检查覆盖 22 行业生成（含 `bento` 便当盒餐厨与 `limestone` 天然石灰石建材）、GEO 五层机器可读端点（`/llms.txt`、`/llms-full.txt`、`/ai/*.json`）、事实撤销、内部资料隔离、HTML 转义、Clean URLs、双模装柜算力（轻泡外箱 + 重货石材 20GP 限重）及边缘防护。

[MIT License](LICENSE) · [第三方许可](THIRD_PARTY_NOTICES.md)。
