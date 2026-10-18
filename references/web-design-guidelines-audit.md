# Vercel Web Interface Guidelines 上线前全域界面体检指南

> **核心来源**：深度融合自 Vercel 实验室官方技能 `vercel-labs/agent-skills/skills/web-design-guidelines`（3.1万+ Star 体系与 `web-interface-guidelines` 规范）。  
> **核心使命**：作为前端页面交付前的“第二轮严格审查（Pre-Flight Check）”，对网页进行可用性、可访问性（a11y）、交互一致性与视觉规范极限体检，确保零明显缺陷上线。  
> **互补协同**：本指南负责“**有没有明显问题**”（质量门禁与体检），与 Anthropic 的 `frontend-design`（负责“**怎么设计**”与反千篇一律）形成无死角闭环。

---

## 1. 交付前体检模式与输出规范 (Audit Protocol & Terse Output)

在执行体检时，必须提供具体 HTML/CSS 文件上下文或运行自动化审计脚本，以高信噪比的 `file:line: [CATEGORY] Rule description` 紧凑格式输出。严禁空泛陈述。

---

## 2. 12 维上线前界面体检清单 (The 12-Dimension Health Check Matrix)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 Vercel 12 维界面体检全景雷达 (Health Check Radar)            │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ 1. Accessibility    │ a11y 标签、语义化 HTML、跳过导航链接、键盘导航支持     │
│ 2. Focus States     │ :focus-visible 环、严禁裸 outline:none、吸顶元素避让 │
│ 3. Forms & Inputs   │ autocomplete、正确 inputmode、不阻断粘贴、行内报错    │
│ 4. Animation        │ 严格尊重 prefers-reduced-motion、严禁 transition:all  │
│ 5. Micro-Typography │ Unicode省略号(…)、弯引号(“”)、不间断空格、tabular-nums │
│ 6. Content Overflow │ 文本截断 line-clamp、Flex 子元素 min-w-0、空状态安全   │
│ 7. Images & CLS     │ 显式 width/height、首屏 fetchpriority="high"、懒加载  │
│ 8. Performance      │ preconnect 关键 CDN、字体 preload、避免布局抖动       │
│ 9. Navigation/State │ URL 同步筛选参数、语义化 <a> 标签、破坏性操作确认     │
│ 10. Touch & Mobile  │ touch-action: manipulation、弹窗 overscroll: contain │
│ 11. Safe Areas      │ 适配 env(safe-area-inset-*)、overflow-x 容器级防横移 │
│ 12. Dark Mode       │ <html> 声明 color-scheme: dark、统一原生控件渲染      │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

### ① 可访问性 (Accessibility / a11y)
- [ ] **语义化优先**：严格使用 `<button>` 处理动作点击，使用 `<a>` 处理路由跳转，严禁用 `<div onclick>` 冒充按钮或链接；
- [ ] **无文字图标按钮**：纯图标按钮（如购物车、搜索、语言切换、关闭弹窗）必须显式添加 `aria-label="Close modal"` 或内部隐藏 `<span class="sr-only">`；
- [ ] **表单控件绑定**：每个 `<input>`, `<textarea>`, `<select>` 必须有明确绑定的 `<label for="...">`，或显式包含 `aria-label`；
- [ ] **装饰性元素隐藏**：纯装饰性的 SVG 图标、背景装饰图形必须添加 `aria-hidden="true"`，防止屏幕阅读器朗读无意义噪点；
- [ ] **图片 alt 属性**：所有 `<img>` 标签必须包含 `alt` 属性。纯装饰图允许 `alt=""`，但不可遗漏属性；
- [ ] **动态更新提醒**：异步消息提示（如 RFQ 提交成功 Toast、实时表单校验报错）容器必须带有 `aria-live="polite"`；
- [ ] **跳过主内容链接**：页面顶部提供 `<a href="#main" class="skip-link">Skip to main content</a>`，方便键盘用户直达内容区。

### ② 聚焦状态 (Focus States & Keyboard Handlers)
- [ ] **显式聚焦指示器**：所有可交互元素（按钮、链接、输入框、Tab 切换卡）必须具备高对比度清晰可见的聚焦环（推荐使用 `:focus-visible`）；
- [ ] **绝对严禁裸 outline: none**：任何写有 `outline: none` 或 `outline: 0` 的地方，必须紧随其后声明可见的 `:focus-visible` 替代样式（如 `box-shadow` 或自定义 `ring`）；
- [ ] **避免鼠标点击出现焦点环**：严格优先使用 `:focus-visible` 而非普通 `:focus`，避免鼠标点击时在普通按钮上留下难看的长久外框；
- [ ] **吸顶元素避让**：固定在顶部的 Sticky Header 或悬浮浮窗绝对不能覆盖正在获得键盘焦点的输入框或链接。

### ③ 表单规范与输入体验 (Forms & Feedback)
- [ ] **自动填充支持**：输入框必须提供标准的 `autocomplete` 属性（如 `name`, `email`, `tel`, `organization`, `street-address`）；
- [ ] **精准 inputmode**：数字输入框配置 `inputmode="numeric"` 或 `inputmode="decimal"`；邮箱配置 `type="email"`；
- [ ] **严禁阻止粘贴**：任何输入框（包括公司税号、邮箱、订单编号）绝对严禁添加 `onpaste="return false;"` 或 `e.preventDefault()` 阻止用户粘贴；
- [ ] **点击命中区域扩大**：复选框 (Checkbox) 与单选框 (Radio) 必须与其文本标签作为一个整体包裹（或用 `htmlFor` 关联），点击文字即触发选中，消除无效死区；
- [ ] **行内报错与自动聚焦**：表单验证失败时，错误信息必须直接显示在对应输入框下方（行内），且提交时焦点自动跳转至第一个报错字段；
- [ ] **防重复提交态**：点击提交后，提交按钮必须立即进入 Loading/Disabled 状态，防止海外网络延迟导致的大量重复下单或重发询盘。

### ④ 动效与无障碍偏好 (Motion & Animation)
- [ ] **严格响应 reduced-motion**：所有 CSS 动画和过渡必须包裹在 `@media (prefers-reduced-motion: reduce)` 内，提供静止替代方案或直接禁用；
- [ ] **严禁滥用 transition: all**：**绝对禁止在 CSS 中书写 `transition: all ...`**！必须显式列出过渡属性（如 `transition: transform 0.2s ease, opacity 0.2s ease`），避免引起全属性重排 (Reflow)；
- [ ] **硬件加速优先**：动效应仅作用于 `transform` 和 `opacity`，严禁对 `width`, `height`, `margin`, `padding`, `top`, `left` 施加连续平滑动画；
- [ ] **动效可中断性**：动效运行期间如果用户产生点击或滚动，界面应能即时响应，不可阻塞主线程。

### ⑤ 微排版与字符规范 (Micro-Typography Specs)
- [ ] **Unicode 省略号**：加载或截断文本一律使用 Unicode 原生省略号 `…`（`\u2026`），严禁使用三个句点 `...`；
- [ ] **正规弯引号**：英文双引号使用 `“` 和 `”`（`&ldquo;` / `&rdquo;`），单引号使用 `‘` 和 `’`，严禁用直引号 `"` 或 `'` 代替正式英文出版物排版；
- [ ] **单位不间断空格**：数字与度量单位之间必须使用不间断空格 `&nbsp;`，防止数字与单位在移动端折行分离（如 `21.5&nbsp;tons`、`40&nbsp;HQ`、`120&nbsp;°C`）；
- [ ] **表格数据等宽排列**：所有数据列、财务报价、库存数量、参数对照表中的数字容器，必须应用 `font-variant-numeric: tabular-nums`，确保小数点与个位十位严格对齐；
- [ ] **标题排版平衡**：关键大标题必须设置 `text-wrap: balance` 或 `text-wrap: pretty`，杜绝标题末行只落单一个单词（孤字寡行 Widows）的丑陋现象。

### ⑥ 内容容错与溢出防断裂 (Content Handling & Overflow)
- [ ] **超长文字自适应**：所有产品名称、买家姓名、公司名称容器必须妥善设置 `truncate`、`line-clamp-*` 或 `break-words`，杜绝长单词撑破外层布局；
- [ ] **Flex 布局防被撑爆**：Flex 容器内的文本子元素必须包含 `min-w-0`，否则其默认 `min-width: auto` 会阻止文本截断生效并导致横向撑破；
- [ ] **空状态容错渲染**：当产品列表无筛选结果或参数项为空时，必须渲染清晰友好的空状态卡片，严禁出现空白漏洞或未捕获的 `undefined` / `NaN`。

### ⑦ 图像规范与视口防抖 (Images & CLS Prevention)
- [ ] **显式宽高防跳动**：所有 `<img>` 标签必须在 HTML 中显式标明 `width="..." height="..."`，或者在 CSS 中配置 `aspect-ratio`，杜绝累积布局偏移（Cumulative Layout Shift, CLS）；
- [ ] **首屏图像优化**：首屏最大内容图像（LCP Hero Image）必须标记 `fetchpriority="high"`，并严禁标记 `loading="lazy"`；
- [ ] **首屏以下懒加载**：首屏以下的所有产品展示图必须标注 `loading="lazy"`。

### ⑧ 性能与关键资产预热 (Performance & Preconnect)
- [ ] **字体域名预连接**：使用外部 Google Fonts 或 CDN 资源时，在 `<head>` 中加入 `<link rel="preconnect" href="...">`；
- [ ] **关键主字体预加载**：对首屏使用的关键西文字体或衬线字体使用 `<link rel="preload" as="font" type="font/woff2" crossorigin>`，并配置 `font-display: swap`，消除字体闪烁（FOIT）；
- [ ] **避免滥用大型动图**：短循环展示优先使用 `<video autoplay muted loop playsinline>` 替代体积庞大且无法暂停的动图 GIF。

### ⑨ 导航规范、状态持久化与 Clean URLs (Navigation, URL State & Clean URLs)
- [ ] **Clean URLs 全局无后缀规范 (Zero .html Extensions)**：所有站内内链 `<a>` 严禁出现 `.html` 后缀（首页一律为 `href="./"` 或 `href="/"`，二级页一律为 `href="products"`、`href="about"`，锚点为 `href="products#kids"`）。页面的 `<link rel="canonical">`、`<meta property="og:url">`、JSON-LD `@id`/`url` 以及 `sitemap.xml` 中的 `<loc>` 必须全部使用干净的无后缀 URL。静态部署必须自带 `vercel.json` (`"cleanUrls": true`)、`nginx.conf` (`try_files $uri $uri.html $uri/ =404;`) 或 `.htaccess` 伪静态规则；
- [ ] **筛选与状态 URL 同步**：多维产品筛选器（如石材表面、规格、包装）、分页等状态必须同步更新到浏览器 URL Query 参数中，便于海外买家直接复制链接发给团队同事打开；
- [ ] **语义化超链接支持**：所有带跳转行为的元素必须使用标准 `<a>` 标签，确保海外买家通过鼠标中键（滚轮点击）或 `Cmd/Ctrl + 点击` 能够在浏览器新标签页正常打开；
- [ ] **高风险操作确认**：清空已选 SKU、清空集装箱配载等破坏性操作，必须提供确认提示窗或短暂的“撤销 (Undo)”机制，严禁立即无预警清空。

### ⑩ 触摸交互与移动端体验 (Touch & Gestures)
- [ ] **双击延迟消除**：按钮与交互控件设置 `touch-action: manipulation`，消除移动端浏览器的 300ms 双击缩放判定延迟；
- [ ] **弹窗滚动穿透防御**：抽屉式规格面板、移动端折叠菜单与弹窗容器，必须配置 `overscroll-behavior: contain`，杜绝滚动到边缘时把底层页面连带拖动的穿透 Bug；
- [ ] **最小可点击尺寸**：所有移动端按钮和图标触控区域，最小物理尺寸不低于 44px × 44px，防止粗手指误触。

### ⑪ 安全区域与全屏适配 (Safe Areas & Layout)
- [ ] **刘海与底部横条适配**：全宽全高界面（尤其是移动端底栏询盘浮条）必须支持 `padding-bottom: env(safe-area-inset-bottom)`；
- [ ] **页面横向滚动彻底封死**：外层容器合理设置 `overflow-x: hidden`，并通过移动端真机或 390px 视口测试，确保在移动端无法左右晃动。

### ⑫ 深色模式与全局主题 (Dark Mode & Theming)
- [ ] **系统配色声明**：在支持深色主题的页面中，必须在 `<html>` 标签或根 CSS 中声明 `color-scheme: dark`，确保原生下拉选择框、滚动条和表单光标自动匹配深色风格，避免暗黑页面出现刺眼的亮白下拉菜单。
