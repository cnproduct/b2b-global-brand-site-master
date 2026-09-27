# B2B Global Brand Site Master · V2

从简单 Logo、企业简介和现有资料，持续完成外贸 B2B 品牌、企业知识库、数字资产与专业独立站。V2 将 `renwork-industry-site-master` 的事实治理和行业采购蓝图，融合进本仓库的品牌取色、静态网站生成、采购交互和执行入口。

**20 类行业蓝图 · 10 类页面模板 · 21 模块知识体系 · 同源事实驱动 HTML / Schema / 搜索文件。**

只有少量资料也能开始：自动生成可运行草稿和资料缺口，再由 Agent 完成研究、品牌设计、真实文案与页面。工厂、认证、参数、客户、价格等未知信息不会从行业模板变成企业事实。生成器不是完整 CMS；Skill 指导 Agent 完成企业项目所需的功能与交付。

## 直接使用

将本仓库作为一个 Skill 文件夹安装到所用 Agent 的 skills 目录，以 [SKILL.md](SKILL.md) 为入口。Codex 默认位置：`~/.codex/skills/b2b-global-brand-site-master/`。

```text
使用 $b2b-global-brand-site-master。
根据这个 Logo、企业简介和已有资料，为公司建立完整的外贸独立站。
识别主营行业和采购路径，完成品牌规范、21模块知识底座、内容与数字资产、
行业页面和代码，执行 SEO/GEO 与询盘验收。未知事实进入内部缺口清单。
先产出首页、代表产品页和询盘流程，再扩展完整站点，不停在方案阶段。
```

Python 3.10+；运行时无强制第三方依赖。已安装 Pillow 时可提取栅格 Logo 颜色，否则明确记录回退；SVG 需单独解析或转换，不冒充已取色。

在 Skill 目录运行：

```bash
python3 scripts/orchestrator.py --name "Example Company" \
  --intro "We supply industrial components." \
  --industry components --out /tmp/example-company-project

python3 scripts/sitekit.py industries
```

Logo 可用 `--logo /path/logo.png` 提供；域名、邮箱、主色可选。初始六页是 **noindex 草稿**，不是成品。Agent 按行业资料编辑 `content/site.json`、核实知识卡并补齐页面。详细字段、素材批准、生成器范围及旧版迁移见 [运行契约](references/runtime.md)。

```bash
python3 scripts/orchestrator.py --project /path/company-project
python3 scripts/orchestrator.py --project /path/company-project --release
```

每次构建返回新的静态目录。只发布这个目录，不能上传整个含 `private/` 的企业项目。`--release` 生成并检查本地发布候选，不自动部署，不代表已收录。

## 深度融合后的能力

| 工作层 | 内容与执行机制 |
|---|---|
| 品牌系统 | 定位、语气、Logo规则、颜色/字体、网页设计规范；取色来源与局部对比度可追溯 |
| 企业知识 | 复用 RenWork V4 七状态、00–20 模块、来源/时效/敏感度；同一事实出口服务所有页面 |
| 行业与内容 | 买家角色、决策路径、参数字段、证据要求、页面顺序、RFQ字段和缺资料策略 |
| 数字资产 | 原始素材、许可、哈希、AI来源、事实关联与公开范围；仅复制本次页面引用的获准文件 |
| 网站实现 | 原生静态HTML、四种采购版式、语义规格表、真实目录路由；按任务扩展产品/应用/技术等页面 |
| 采购转化 | 基础真实邮箱联系；完整RFQ按实际后端接通；可选装柜容量下界估算，考虑体积与重量 |
| SEO / GEO | 页面意图、内链、canonical、robots、sitemap、同源结构化数据；llms.txt / WebMCP按需使用 |
| 质量与运营 | 可执行文件/链接/锚点/索引状态检查；搜索展示、AI引用、访问、询盘分别验收 |

不再生成默认证书、虚构工程师、假手机号、无后端表单、假价格，或重复文本凑 `llms.txt` 长度。不存在“100 分即保证被 AI 引用”的验收。

## 行业模板

以下是采购蓝图，不是 20 套已在真实客户上线验证的皮肤。行业知识不代表目标公司的能力；真实公司仍需核实 SKU、材料、标准和市场要求。

| 行业 ID | 范围 | 采购路径 |
|---|---|---|
| `machinery` | 工业机械与自动化 | 工况→机型→系统配套→验收→服务 |
| `components` | 五金与精密零部件 | 图纸→材料→公差→工艺→批量 |
| `building-materials` | 建材与装饰材料 | 应用→材质→性能→安装→样板 |
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

完整字段见 [行业数据](assets/industries.json)；10 类页面和品牌交付见 [页面蓝图](references/site-blueprints.md)。

## SEO / GEO 的更新依据

核验日期 **2026-09-27**，后续项目仍需复查官方更新：

- Google AI 搜索仍重视基础 SEO、原创且有用的信息，不要求专用 AI Schema、固定字数或 `llms.txt`。见 [Google 官方指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)。
- 纳入 Google 生成式 AI 展示报告/独立控制及 Bing AI Performance 更新；以目标账号实际字段为准。曝光、引用与询盘不得混算。见 [Google 报告](https://support.google.com/webmasters/answer/16984139)、[Bing 更新](https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/)。
- 搜索爬虫、训练爬虫、用户触发访问分开处理；不把开放 GPTBot 作为 ChatGPT 搜索的必要条件。见 [OpenAI 爬虫](https://developers.openai.com/api/docs/bots)。
- `llms.txt` 是可选公共目录；WebMCP 是按当前支持情况选择的交互能力。FAQ 为买家提供信息，不承诺已停用的 Google FAQ 富媒体展现。

完整的结论、时效冲突和原始链接见 [官方核验表](references/search-current.md)、[发布清单](references/search-release.md) 与 [锁定来源](references/sources.json)。

## 验证和维护

```bash
python3 tests/check_pipeline.py
python3 tests/check_validator.py
node tests/check_estimator.mjs
```

Node 18+ 用于估算器测试。检查覆盖 20 行业生成、事实撤销、内部资料隔离、HTML转义、资产/域名边界、真实链接、草稿/发布状态以及装柜计算。

这些检查只证明对应本地行为；浏览器审查、公网HTTP、表单收件、GSC收录、AI引用与转化必须在实际企业项目另外运行。完整变更与迁移说明见 [V2融合记录](references/fusion-v2.md)。

[MIT License](LICENSE) · [第三方许可](THIRD_PARTY_NOTICES.md)。未复制无明确许可的 SEO 优化器源码。
