# 实战失败案例复盘与不可违反质检军规 (Failure Cases & Strict Guardrails)

在多个真实 B2B 出海独立站（如 `tianyalimestone.com`、`custombentofactory.com`）的构建、发布与运维历史中，曾发生过 6 类极具代表性的工程与业务失误。本规范将其转化为全行业强制执行的**不可违反防错军规（Strict Guardrails）**。

---

## 💥 案例 1：Canonical URL 缺少斜杠导致全站死链 (URL Slash Concatenation Glitch)

### 1. 现象复盘
在生成 Schema.org `ItemList`、`<link rel="canonical">` 或 `/ai/products.json` 时，若直接使用朴素字符串拼接：
```python
# ❌ 错误写法：
url = f"{domain}{page_path}"
```
当 `domain` 为 `https://example.com` 且 `page_path` 未以斜杠开头（如 `products/item`）时，会生成形如 `https://example.comproducts/item` 的畸形死链。

### 2. 不可违反防错军规 (Guardrail 1)
> 🚨 **军规 1**：全站所有域名与路径拼接必须统一通过 `scripts/design_math.py` 中的 `safe_urljoin(domain, path)` 或等价防御逻辑：
> ```python
> python3 scripts/design_math.py safe-url https://example.com products/item
> ```
> 发布前必须运行 `scripts/validate_site.py --release --domain https://...`，校验所有 Canonical、Sitemap 与内链格式合法且无 `.html` 后缀残留。

---

## 💥 案例 2：微距产品特写与空间应用场景图脱节 (Material & Scene Disconnect)

### 1. 现象复盘
在批量生成或匹配产品详情页图片时，曾出现产品微距特写是“温润焦糖黄滚磨仿古面”，但配套的 3D 空间渲染图却是“浅灰白色现代抛光大板”，被专业买手一眼识破为虚假拼凑。

### 2. 不可违反防错军规 (Guardrail 2)
> 🚨 **军规 2（图实一致性铁律）**：
> 1. **特写图锁定真实源头**：主力产品微距/结构特写优先使用工厂实拍原图；AI 概念图必须显式标记 `is_ai_generated: true` 且不得冒充实拍厂房、检测报告或证书；
> 2. **场景生成强约束**：配套场景图必须在色彩（色差 $\Delta E < 5$）、表面肌理（亚光/抛光/滚磨/防滑纹）、结构分格与边缘处理上与该 SKU 特写 **100% 像素级对齐**；
> 3. **逐款核查闸门**：上线前逐一点击核查每个 SKU 详情页，严禁跨款式混用场景图。

---

## 💥 案例 3：轻泡货习惯套用重货，导致集装箱超重爆柜 (Deadweight Cargo Blindspot)

### 1. 现象复盘
若按常规外贸体积（20GP 容积 `33.1 CBM`）推算高密度产品（如天然石材 $\rho = 2,620\text{ kg/m}^3$），会得出 20mm 石板可装 `1,400 m²` 的荒谬结论——实际总重将高达 `73.3 吨`，超过港口与海运安全限重（`26.5 吨`）近 3 倍。

### 2. 不可违反防错军规 (Guardrail 3)
> 🚨 **军规 3（双模装柜算力隔离）**：
> 1. **重货行业（石材、板材、金属铸件、瓷砖）**：必须调用重货模式 `python3 scripts/design_math.py stone-container --area 480 --thickness 20`，以 **20GP 最大安全载重（26.5 吨）** 为硬瓶颈（20mm 石板单柜安全上限约 `480–504 m²`，30mm 约 `320–336 m²`）；
> 2. **轻泡/外箱行业（便当盒、餐厨、家电、箱包）**：调用外箱模式 `python3 scripts/design_math.py container --length ... --width ... --height ... --weight ... --pcs ...`，同时比较体积上限与载重上限（取 `min(by_volume, by_weight)`）。

---

## 💥 案例 4：第三方静态表单中继丢信与被刷爆 (Form Relay Failure)

### 1. 现象复盘
依赖免配置第三方公共表单中继（如未验签的公共网关）时，常出现通知邮件被海外反垃圾组织拦截、机器人脚本批量灌水，以及前端在后端失败时仍显示“发送成功”导致高意向大客户流失。

### 2. 不可违反防错军规 (Guardrail 4)
> 🚨 **军规 4（真实询盘闭环与三段式验收）**：
> 1. 未配置真实后端时，必须诚实使用 `email_draft` 模式（拉起买家本地邮件草稿），绝不伪装“已自动收到询盘”；
> 2. 启用 `http` 模式时，推荐采用第一方 Cloudflare Worker `/api/inquiry` + Turnstile 服务端验签（`siteverify` + `CF-Connecting-IP`）+ 隐形蜜罐字段；后端投递失败必须返回非 2xx 错误，前端保留用户输入供重试；
> 3. **三段式端到端验收**：① 假 token 探针返回 `403` $\rightarrow$ ② 真机浏览器人工通过 Turnstile 提交成功 $\rightarrow$ ③ 客户收件箱确认收到真实邮件。

---

## 💥 案例 5：CDN 边缘缓存旧 CSS 导致排版错乱与抽屉铺屏 (FOUC & Cache Poisoning)

### 1. 现象复盘
网站更新 HTML 结构后，由于 Cloudflare 等 CDN 默认缓存静态 `/css/site.css`，访客浏览器加载了“新 HTML + 旧 CSS”，导致隐藏的移动端抽屉导航、指南针弹窗或带 emoji 的列表直接裸露铺满首屏。

### 2. 不可违反防错军规 (Guardrail 5)
> 🚨 **军规 5（Anti-FOUC 四大防线）**：
> 1. **内容哈希缓存穿透**：所有 CSS/JS 引用必须携带内容哈希或构建版本号（如 `/css/site.css?v=a1b2c3d4`）；
> 2. **防御性内联隐藏**：所有弹窗、移动抽屉、折叠面板必须带有 `hidden` 属性，并在 `<head>` 内联 `<style>[hidden],.modal:not(.active),.drawer:not(.active),.mobile-drawer:not(.active){display:none!important}</style>`；
> 3. **字符集与图标安全**：`<head>` 前 1024 字节内强制声明 `<meta charset="utf-8">`，导航图标优先使用内联 SVG，杜绝生僻 Emoji 跨平台乱码；
> 4. **分级缓存响应头**：HTML 响应头设为 `Cache-Control: no-cache, no-store, must-revalidate`。

---

## 💥 案例 6：多智能体/多会话并发修改导致代码覆盖 (Multi-Agent Collision)

### 1. 现象复盘
在多会话协同维护同一生产站点时，若直接用本地旧副本上传覆盖远程构建器脚本，会抹掉前序会话已完成的新增页面或 GEO 配置。

### 2. 不可违反防错军规 (Guardrail 6)
> 🚨 **军规 6（并发校验与备份）**：
> 1. 每次构建均生成独立输出目录（拒绝静默覆盖已有构建目录）；
> 2. 维护线上生产构建器前，先核对文件哈希（`md5sum` / `sha256sum`）并在服务端创建带时间戳备份，确认无冲突后再执行增量更新与全量回归校验。
