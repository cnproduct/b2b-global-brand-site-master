# 01. 品牌视觉 DNA 提取与设计变量桥接规范 (Brand Visual DNA Bridge)

本规范定义了从企业输入的极简 Logo（PNG/JPG/WEBP/SVG）中自动化解构视觉特征，并推导出符合国际 W3C DTCG 规范与 WCAG 无障碍标准的完整设计系统。

---

## 一、数学色彩模型与 60-30-10 空间分配

系统依据色彩动力学（Color Kinetics）与 B2B 工业审美，严格遵循以下算法推导：

### 1. 主色聚类与提取
- **色彩聚类**：采用 $k$-means 算法提取输入 Logo 的前 5 种高频像素色，过滤极端高亮（$L > 0.95$）与纯黑透底杂色；
- **主导品牌色 ($C_{primary}$)**：取色相饱和度与占比权重综合最高者；
- **互补/协调强调色 ($C_{accent}$)**：在 CIELAB 色彩空间中以原色色相环顺时针或逆时针旋转 $150^\circ \sim 180^\circ$ 计算高对比行动色，专门用于高转化 CTA（如 "Request Sample Kit", "Calculate Freight"）。

### 2. 60-30-10 工业布局配比
- **60% 基底与承载表面（Dominant Neutral）**：
  - 浅色模式：工业冷白 `oklch(0.985 0.005 240)` 或极淡蓝灰；
  - 深色模式（沉浸式控制台）：深海蓝灰 `oklch(0.18 0.03 245)`；
- **30% 结构层与品牌基调（Secondary / Structural）**：
  - 卡片边框、Bento 栅格轮廓、导航底色、次级标签、数据指标大字；
- **10% 转化焦点色（High-Conversion CTA）**：
  - 核心操作按钮、高光指示灯、WebMCP 交互表单焦点。

---

## 二、WCAG 2.1 AA/AAA 级对比度强制矫正

任何对外展示的文字与按钮必须通过严格的数学对比度验证：

$$\text{Contrast Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$

其中 $L$ 为相对亮度（Relative Luminance）：
$$L = 0.2126 \times R_{sRGB} + 0.7152 \times G_{sRGB} + 0.0722 \times B_{sRGB}$$

### 质量守护者门禁规则：
1. **正文文本**：对比度必须 $\ge 4.5:1$（AA 级标准）；
2. **大型标题与核心数字**：对比度必须 $\ge 3.0:1$；
3. **若 Logo 提取的品牌色为亮黄、浅绿或低对比色**：
   - 系统自动激活**防眩光保护胶囊（Pill Capsule Protection）**：在文字下方自动衬垫深色墨黑底托，或将该颜色自动降调至可读深调；
   - 按钮文字自动在纯白 `#FFFFFF` 与极夜黑 `#111827` 之间动态切换，确保绝对可读。

---

## 三、W3C DTCG 兼容的标准 Design Tokens (`tokens.css`)

编译输出的 CSS Variables 直接无缝对接现代前端与 Tailwind CSS：

```css
:root {
  /* 品牌核心变量 - 动态自 Logo 提取 */
  --brand-primary: #0F52BA;
  --brand-primary-rgb: 15, 82, 186;
  --brand-accent: #FF6B35;
  --brand-accent-hover: #E85A24;
  --brand-surface: #F8FAFC;
  --brand-surface-card: #FFFFFF;
  --brand-border: #E2E8F0;
  
  /* 文本系统 */
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-muted: #94A3B8;
  --text-inverse: #FFFFFF;
  
  /* 工业字体阶梯 (Modular Typography Scale - 1.25 Ratio) */
  --font-display: "IBM Plex Sans Condensed", "Inter", -apple-system, sans-serif;
  --font-mono: "IBM Plex Mono", "SF Mono", monospace;
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1.0rem;   /* 16px */
  --text-lg: 1.25rem;    /* 20px */
  --text-xl: 1.563rem;   /* 25px */
  --text-2xl: 1.953rem;  /* 31.25px */
  --text-3xl: 2.441rem;  /* 39px - 核心硬核指标看板大字 */
  
  /* 布局与圆角规范 (严禁泡泡式夸张大圆角) */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --radius-full: 9999px;
  
  /* 阴影：微弱精准描边优于模糊扩散阴影 */
  --shadow-bento: 0 1px 3px rgba(0, 0, 0, 0.05), 0 0 0 1px var(--brand-border);
  --shadow-elevated: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 0 0 1px var(--brand-border);
}
```

---

## 四、3D 工业实景 AI 提示词工程 (Midjourney v6 / FLUX.1)

为了解决企业“没有实测高清厂房大图与实验室照片”的尴尬，本系统将自动推导出 4 大核心视角的工业级渲染 Prompt 矩阵：

1. **自动化智造车间 (Automated Smart Factory)**：
   > `Ultra-realistic architectural photography of a modern high-end manufacturing facility for [INDUSTRY], robotic assembly lines with precision orange arms, epoxy grey industrial floor with reflective sheen, 5000K overhead LED continuous linear lighting, pristine cleanroom environment, employees in professional technical uniform, shot on Hasselblad H6D-100c, 24mm wide angle lens, f/8, natural diffused lighting, 8k resolution, cinematic industrial aesthetic --ar 16:9 --style raw`

2. **国家级/CNAS 质检实验室 (CNAS Testing Laboratory)**：
   > `Professional commercial photography of an advanced B2B quality control laboratory for [INDUSTRY], testing rigs, automated tensile test apparatus, calibrated digital micrometer displays, certified testing engineer in clean lab coat conducting strict quality inspection, high-tech clean background, ISO/IEC 17025 accredited atmosphere, neutral lighting, 50mm lens, tack-sharp focus --ar 16:9 --style raw`

3. **海外采购样件展陈台 (Procurement Vignette & Sample Box)**：
   > `Studio product photography of an architectural materials sample kit box on a minimalist slate podium, precision cut swatches, embossed matte black packaging with gold foil logo of [BRAND_NAME], detailed technical specification cards with millimeter callouts, soft directional studio lighting, shallow depth of field, 85mm macro lens, ultra crisp textures, luxury industrial feel --ar 16:9`

4. **全球海运集装箱重载装运 (Port Logistics & Heavy Freight)**：
   > `Aerial drone high-angle view of a large-scale manufacturing logistics hub, export pallets securely shrink-wrapped with branded cargo tape [BRAND_NAME], heavy-duty forklift loading 40HQ ocean shipping containers, deep harbor container terminal in the soft morning fog, high dynamic range, industrial shipping scale, 4k --ar 16:9`
