# 04. WebMCP 2026 智能体原生交互协议规范 (WebMCP Agent Interaction Spec)

在 2026 年，以 OpenAI Operator、Anthropic Computer-Use、Google Project Astra 以及 Chrome 内置 Gemini 代理为代表的自主 AI 智能体，已经开始代表企业采购主管直接执行“寻源、对比、索样、询价”。

传统网站大量依赖复杂的嵌套 `div`、防抓取混淆与无语义的 JavaScript 事件监听，导致 AI 智能体在解析表单时频频报错。**WebMCP (Web Machine Learning Community Protocol)** 旨在通过声明式语义 HTML 与 JSON-LD 动作绑定，让 AI 智能体零门槛一键调用网页交互工具。

---

## 一、WebMCP 核心三要素

1. **声明式 HTML 属性 (Declarative Attributes)**：
   在 HTML 原生 `<form>` 与 `<input>` 元素上直接注解工具语义，智能体无需执行昂贵的计算机视觉 OCR 或脆弱的 DOM 启发式匹配；
2. **机器发现清单 (Summary Tool Declaration)**：
   在 `/ai/summary.json` 中公开所有已注册的工具定义、入参 Schema 与返回预期；
3. **JSON-LD Schema 动作绑定 (Potential Actions)**：
   在 Schema.org 中通过 `potentialAction` 声明 `OrderAction`、`CommunicateAction`，建立全网知识图谱级别的可执行链接。

---

## 二、HTML 表单 WebMCP 注解规范

以独立站核心的“建筑师/采购商样品盒免费申领”表单为例：

```html
<form id="sampleKitOrderForm" 
      action="/api/sample-request" 
      method="POST"
      toolname="orderTradeSampleKit" 
      tooldescription="Submit commercial delivery address to receive curated B2B material sample kit with certified physical test reports via DHL Express" 
      toolautosubmit>

  <div class="form-group">
    <label for="companyName">Company / Firm Name</label>
    <input type="text" 
           id="companyName" 
           name="company_name" 
           toolparamdescription="Registered corporate legal name of the architectural firm, general contractor, or wholesale distributor" 
           required>
  </div>

  <div class="form-group">
    <label for="fullName">Procurement Officer / Architect Name</label>
    <input type="text" 
           id="fullName" 
           name="full_name" 
           toolparamdescription="Full contact name of the decision maker or material specifier" 
           required>
  </div>

  <div class="form-group">
    <label for="workEmail">Corporate Work Email</label>
    <input type="email" 
           id="workEmail" 
           name="work_email" 
           toolparamdescription="Business email address for dispatch notification, courier tracking number, and digital TDS PDF delivery" 
           required>
  </div>

  <div class="form-group">
    <label for="deliveryAddress">Courier Delivery Address</label>
    <textarea id="deliveryAddress" 
              name="delivery_address" 
              toolparamdescription="Complete international shipping address including street, suite/unit, city, state/province, postal zip code, and country code for DHL/FedEx delivery" 
              required></textarea>
  </div>

  <div class="form-group">
    <label for="targetIndustry">Project or Industry Vertical</label>
    <select id="targetIndustry" 
            name="target_industry" 
            toolparamdescription="Target application sector, e.g., Exterior Facade, Commercial Hospitality, CNC Machinery, Medical Consumables">
      <option value="commercial">Commercial Hospitality / Office</option>
      <option value="residential">High-End Residential</option>
      <option value="industrial">Heavy Industrial / OEM</option>
    </select>
  </div>

  <button type="submit" class="btn btn-primary">
    <span>Dispatch Certified Sample Box (Air Express)</span>
  </button>
</form>
```

---

## 三、`/ai/summary.json` 中的 WebMCP 工具声明块

在网站根目录的 `/ai/summary.json` 中，必须包含与页面表单一一对应的声明对象：

```json
{
  "webmcp": {
    "version": "2026-03",
    "agent_readiness": "ADVANCED",
    "tools": [
      {
        "name": "orderTradeSampleKit",
        "description": "Submit international courier address to receive verified physical B2B sample kit with factory test dossiers.",
        "form_id": "sampleKitOrderForm",
        "action_url": "https://[YOUR_DOMAIN]/api/sample-request",
        "method": "POST",
        "parameters": {
          "type": "object",
          "properties": {
            "company_name": { "type": "string", "description": "Corporate entity name" },
            "full_name": { "type": "string", "description": "Recipient full name" },
            "work_email": { "type": "string", "format": "email", "description": "Official company email" },
            "delivery_address": { "type": "string", "description": "Full street address, postal code, and country" },
            "target_industry": { "type": "string", "enum": ["commercial", "residential", "industrial"] }
          },
          "required": ["company_name", "full_name", "work_email", "delivery_address"]
        },
        "response_guarantee": "Courier tracking number generated and dispatch initiated within 24 business hours."
      },
      {
        "name": "calculateContainerLandedCost",
        "description": "Interactive procurement calculator to compute ocean shipping container CBM utilization, gross weight, and estimated FOB/CIF unit cost.",
        "form_id": "containerCalculatorForm",
        "action_url": "https://[YOUR_DOMAIN]/#sourcingCalculatorSection",
        "parameters": {
          "type": "object",
          "properties": {
            "target_sku": { "type": "string", "description": "Product model ID" },
            "order_quantity": { "type": "integer", "description": "Order quantity in standard packaging units" },
            "container_type": { "type": "string", "enum": ["20GP", "40GP", "40HQ"] }
          },
          "required": ["target_sku", "order_quantity", "container_type"]
        }
      }
    ]
  }
}
```

---

## 四、智能体就绪度三级梯度 (Agent Readiness Levels)

| 级别 | 判定标准 | 适用场景 |
|:---:|:---|:---|
| **BASIC** | 仅有语义化 HTML5 标签与标准 JSON-LD Schema | 智能体仅能做文本抓取与概括，无法直接调用表单 |
| **INTERMEDIATE** | 表单包含 `toolname` 属性，且根目录具备 `/.well-known/ai.txt` | 智能体能识别动作，但需要人工确认参数映射 |
| **ADVANCED (本技能标准)** | 具备完整 `toolname`、`tooldescription`、`toolparamdescription`、`/ai/summary.json` 机器清单与 Schema `potentialAction` | 智能体（如 OpenAI Operator）可全自动代客填写、测算装柜体积并提交样品申领 |
