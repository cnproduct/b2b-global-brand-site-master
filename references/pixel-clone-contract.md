# 复刻基线与原创站的不同验收契约

## 复刻基线

先记录范围、路由、模板、产品与语言。完整整站要实现全部约定路由及功能；模板抽样只减少重复浏览器检查，不减少实现范围。原始证据只读，资源 manifest 记录 URL、最终 URL、类型、状态、路径、sha256 与许可；源代码与运行时结论可回到文件/行号/网络或帧记录。

截图需同视口、浏览器缩放、设备比、字体加载、内容、滚动位置与交互状态；至少桌面和 390×844，其他断点按参考站与风险增加。记录原站自身的重复截图噪声，动画冻结只用于双方相同的对照条件，同时另测真实动效。不得只截首屏、不等字体或拿空白帧作通过证据。

修复顺序：画布/gutter → section 高度/位置 → 列宽/媒体包围盒 → 文本块与换行 → 字体/颜色 → 阴影细节。布局蓝图是测量规格，不是自造参考。优先真实素材与 computed styles，不用目测接近色或默认主题。图片实际 URL 应返回正确媒体类型，不接受 SPA fallback。

图像差分只是诊断；有工具才报告真实 diff 和条件，不宣称任意 98% 通用门槛。保真要求覆盖布局、内容、真实资源、交互状态、响应式与源行为；设计评审与像素数值并列，不能删图片或隐藏控件压低 diff。复杂 WebGL 要解释机制，再做最小重放/数值与帧对齐，不通过亮度、速度、噪声补偿坐标或时序错误。

真实表单、筛选、排序、分页、菜单、错误、空状态与焦点必须是 HTML/组件。保留原应用的 API、校验、数据流、权限、props、事件与 ref；只改展示层时不能改业务契约。第三方后台或模拟接口明确标 DEMO，不称生产可用。

## 原创站

依据 ORIGINALITY.md、目标企业事实和 TRAFFIC_MAP.md 验收，不与参考站要求像素相等。逐项检查目标品牌/域名/联系端点、产品/语言覆盖、原创内容/影像/构图、主要应用路径、采购信息、移动阅读、键盘与 reduced-motion。

复刻基线不通过时继续修复；确实受阻则明确 baseline partial/blocked，已实现的原创站可独立测试，但不能倒推基线 passed。历史模板演示也不能作为原站截图基线。

## design-qa.md 的最小记录

```text
scope / source version / target version / preview URL
routes: known / required / implemented / tested / blocked
products and locales: required / implemented / tested
baseline_result: passed | partial | blocked
original_result: passed | partial | blocked
check | phase | URL/state | viewport/tool | expected | observed | evidence | status
```

状态为 PASS/FAIL/NOT_RUN/BLOCKED。局部测试不得名为 full-site。分别保留 build、资源、console、真实菜单/筛选/空状态、键盘、表单校验/错误/重试和提交接收证据；没有收件测试不能写“邮件已发送”。静态 HTML 审计不检测几何溢出、真实加载、可访问性完整性、平台索引或 AI 引用。

公开发布还需核对主域/www/TLS/redirect、canonical/noindex/robots/sitemap、实际公开正文、schema 及部署版本；域名注册不是部署。GSC/Bing 收录、AI 引用、分析归因与合格询盘按各自证据独立列出。
