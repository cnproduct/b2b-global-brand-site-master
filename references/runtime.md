# V2.1 运行契约与迁移

## 环境与初始化

Python 3.10+；运行时只用标准库，Pillow 为 Logo 位图取色的可选已有依赖。未安装或 SVG 无法解析时明确记 neutral_fallback，不静默声称已提取。Node 18+ 仅用于装柜与询盘模块测试。

`orchestrator.py --name ... --intro-file ... --industry ... --logo ... --out ...` 初始化新项目并编译草稿。也支持 `--intro` 字符串；logo/domain/email 可缺省，不能借用示例值。`--brand-color '#163D48'` 可指定经审查的颜色。未知行业报错，Agent 应先识别行业或在资料中扩展配置。

```
company-project/
  project.json                  # 身份、tenant、域名、联系信息和批准状态
  DESIGN.md                     # 首次生成的设计建议，后续不覆盖
  industry.json                 # 行业采购建议，不是公司事实
  private/
    raw/                        # Logo/简介原件，绝不整体公开
    knowledge-cards.json        # RenWork V4事实卡
    module-coverage.json        # 21模块覆盖与缺口
    asset-register.json         # 图片/文件许可、哈希和发布范围
    gaps.md                     # 当前行业字段与证据缺口
    public-export-report.json   # 被过滤的卡及原因
    brand-tokens.json           # 颜色来源与局部对比度检查
    latest-build.json
    local-validation.json
  content/
    site.json                   # 唯一可编辑页面模型
    public-facts.json           # 每次构建从知识卡重新生成，勿手改
    page-manifest.json          # 页面与claim/asset映射
  builds/site-<unique>/          # 本次唯一公开静态资产目录
  private/deploy/edge-<unique>/  # 默认防护发布包，引用上述静态资产
  private/protection-status.json # 配置生成和运行时防护状态分开
  acceptance.md
```

初始化拒绝覆盖；重建用 `--project company-project`。每次生成全新 build，旧 build 是历史版本；撤销事实后必须部署新的完整输出并清除 CDN/旧下载，不可只更新内部卡。构建出错不得发布失败目录或沿用旧报告。多次构建的历史公开文件仍需由发布流程负责撤下。

本地预览只服务命令返回的 `site_directory`，不要服务整个企业项目：

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory /path/company-project/builds/site-unique
```

在浏览器打开 `http://127.0.0.1:8000/`。本地通过不代表域名、CDN或公网联系渠道已通过验收。

## 页面模型

`content/site.json` 的 pages 为数组，每个 slug 使用英文小写短横线和可选子目录；首页为空字符串。实际输出 `products/item/index.html`，导航/canonical/sitemap 都为 `/products/item/`，无需服务器 rewrite。

最小编辑示例（RW ID 必须换成本项目真实存在的已批准卡）：

```json
{
  "llms": false,
  "training_bot_policy": "unspecified",
  "primary_color": "#163D48",
  "logo_asset_id": null,
  "pages": [{
    "slug": "",
    "type": "home",
    "title": "Company | Product category",
    "description": "A reviewed page description.",
    "heading": "A clear buyer-oriented heading",
    "reviewed_for_public": false,
    "sections": [
      {"kind": "editorial", "heading": "How to select", "text": "Useful selection guidance.", "reviewed_for_public": false},
      {"kind": "facts", "heading": "Company facts", "claim_ids": ["RW-ABC123-0001"]},
      {"kind": "specifications", "heading": "Specifications", "claim_ids": ["RW-ABC123-0002"]}
    ],
    "asset_ids": [],
    "estimator": false
  }]
}
```

- `facts` 直接输出卡的 title/conclusion/conditions，`specifications` 用相同字段生成可横滑的语义表格。不会从模板补参数。
- `editorial` 是纯文本，全部 HTML 转义。Agent 根据买家问题编写有用解释；如果涉及企业事实，同样改用 claim 引用或在人工审核时核对。布尔批准标记本身不是真实性证明。
- title、description、heading、导航文字也属于审核对象，不能在未挂 claim 的标题里塞入“认证”“第一”“免费”等无依据承诺。
- 基线编译器只自动提供保守 WebPage/Organization JSON-LD。需要 Product/Article/BreadcrumbList、hreflang、产品过滤、FAQ、视频、CRM接收后端时由 Agent 按页面模板与真实数据实现和测试，不能将基线编译器描述为完整 CMS 或所有 Schema 自动完成。
- 10 类页面蓝图指导完整内容实现；六页默认稿仅是启动阶段，Agent 应补齐任务所需的真实页面，而不是机械维持六页。

## 事实、素材与发布候选

公开卡通过 sitekit 的共享过滤器（同一 tenant、fact、已验证/公开事实、public、布尔批准、有来源、未过期等）。完整 V4 Schema 随包提供；过滤器只验证公共出口的必要字段，完整知识库可用项目已有 JSON Schema 校验器验证。

图片/下载必须在 private/asset-register.json：company_id匹配，approval=approved，visibility=public，rights_status为owned/licensed/permission_granted，rights_evidence非空，file在当前项目内，sha256与当前文件一致。发布仅复制页面引用的文件。基线允许PNG/JPEG/WebP/PDF；SVG原件保持私有，需经过独立消毒/转栅格后再作为公共图。不要仅修改后缀冒充安全图片。文件真实内容与许可需要人工复核。

`logo_asset_id` 引用获准位图 Logo；未提供不会伪造 Logo 路径。无图片权利材料时继续设计并列缺口，不用图库示意冒充工厂实拍。

release 所需配置：project.json 中明确 domain（HTTPS源站）、contact（真实邮箱）、identity_approved=true、contact_approved=true；至少有一条公开事实；所有页面及编辑段审核通过；引用的事实和素材仍有效。用户已明确为公开建站提供的普通身份和联系方式可记录现有授权后设置，不重复问相同许可。关键资质/性能不得因此批量批准。

```bash
python3 scripts/orchestrator.py --project /path/company-project --release
```

`--release` 生成可审查的本地发布候选，并不自动部署、发消息或修改云端爬虫策略。draft 含 noindex、禁止抓取及空sitemap；release输出规范URL与索引文件。`llms=true` 只生成精简公共导航，不导出完整内部卡。

V2.2 所有构建默认生成 `deployment_directory`：Worker先执行、公开路径白名单、边缘限流和安全响应头。默认通过它部署所引用的静态资产；只上传HTML没有运行时防护。新增 `protection_runtime` 输出恒为NOT_RUN直到实际部署另行验证。旧V2内容模型无需加字段；每次生成新防护配置，已有线上额度/服务绑定/域名配置由发布流程有意识地保留并重新验证。详见 [默认防护与托管契约](site-protection.md)。

training_bot_policy 为 unspecified/allow/disallow，仅控制额外 GPTBot 规则；其它平台/Google独立控制由项目检查当前规则后配置。unspecified 不写额外训练bot指令，并不构成禁止训练。搜索目标与训练意愿都应在发布清单写明。

## V2.1 设计与询盘字段

兼容 V2 的 content/site.json；缺省采用邮件草稿模式，不自动接入服务或发信。

- `page.hero_asset_id`：已批准素材台账内的图片 ID，与普通素材共享许可/哈希/事实撤销检查。不能是PDF；首屏图不懒加载。台账可提供真实的正整数 `width/height` 及准确 `alt_text`，不能猜产品尺寸或把图片像素当产品规格。
- `page.in_navigation`：默认 true。产品详情可设 false，经分类/产品链接进入，避免把全部 SKU 塞入顶栏。当前页有 aria-current。
- `page.type="product"` 的主要询盘 CTA 带产品标题到联系人页面；只预填空白需求框，不覆盖已输入内容。
- `links` 区块包含 heading、reviewed_for_public 和 items；item 为 `{"slug":"products/item","label":"Product title","description":"Reviewed description","claim_ids":[]}`。目标必须是本项目真实页面，说明涉及事实时填写 claim_ids，发布前审核。
- 页面文字、标题和图片保持原公开事实契约。基础界面按钮为英文；生成中文/其他语言网站时 Agent 还需翻译实际 UI 与文案，不把字体/RTL支持称作完整多语言站。

`inquiry` 默认配置：

```json
{"mode":"email_draft"}
```

表单整理姓名、邮箱、需求，选填公司/国家/数量。提交按钮仅在增强脚本成功绑定后启用；脚本不可用时保留显式邮箱入口，不把原生表单误投到JSON端点。单击 Open email draft 打开邮件应用，用户自行确认发送；网页没有发送邮件，也不保存表单草稿到浏览器存储。无邮件应用时使用显式邮箱联系。

HTTP 模式只有已部署真实接收端、确认数据使用说明后配置：

```json
{"mode":"http","endpoint":"/api/inquiry","endpoint_approved":true,
 "privacy_notice":"Replace with a reviewed notice describing your actual data use and recipient."}
```

示例路径只是契约示意，包内不提供该后端。端点接受同源路径或明确HTTPS地址，不接受凭据、查询中的密钥、fragment或协议相对地址。前端 JSON POST 为 name/email/requirements/company/quantity/country；后端需实际校验/限流/防垃圾，持久接收后返回 2xx JSON `{"accepted":true,"reference":"actual-record-id"}`，失败返回非2xx。不要用任意200或演示编号冒充真实接收。

跨域接收须正确配置CORS；同源使用实际CSRF策略；浏览器honeypot不是服务端反垃圾系统。前端15秒无确认可重试，但超时并不证明服务端未收到；跨重试/重载去重由真实后端按业务实施。前端仅阻止同一在途请求及已确认后同一载荷重复发送。不要把回执等同于邮件到达。

本地/浏览器测试只向隔离的本地 mock 发送合成内容；真实外部发信或CRM写入须有该操作的授权。按钮尺寸、错误关联、焦点、缩放和中文/RTL检查见 [网页设计验收](web-design.md)。

## V1 迁移

旧 `export_kb.json` 不能直接导入并保留 Verified 标记，因为它含自动合成数值和承诺。回到原始企业文件重新建卡，旧输出仅作不可信参考。旧示例从新版包移除，Git历史保留基线。

保留原 orchestrator 的 name/intro/industry/domain/email/logo/out 参数；增加 intro-file/project/release/site-out/brand-color。输出从单目录改为私有项目+独立build；旧命令首次生成草稿。

安全别名：stone_cladding→building-materials；consumer_electronics→electronics；auto_parts→automotive；eco_packaging→packaging；solar_energy→energy；home_appliances→appliances；pet_products→pet-products。hygiene_medical、chemicals_pharma 太宽泛，明确报错并要求 Agent 选择具体品类，不能默默落到机械。

旧 kb_synthesizer.py、llms_geo_compiler.py 和 validate_site_100.py 被统一事实出口、同源编译器和 validate_site.py 替代，不保留可能绕过审核的旧生成入口。迁移不是自动删除现有企业站点。
