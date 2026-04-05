# 🏗️ SyncBridge AI - Architecture

## System Overview

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend   │────▶│   Backend API    │────▶│   AI Pipeline   │
│   (React)    │◀────│   (FastAPI)      │◀────│  (HuggingFace)  │
└──────────────┘     └──────────────────┘     └─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐
       │ Adapters │    │ Security │    │ Storage  │
       │ Registry │    │  Layer   │    │(In-Memory)│
       └──────────┘    └──────────┘    └──────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React + TypeScript + Vite | Dashboard UI |
| **Styling** | Tailwind CSS + Framer Motion | Modern animations |
| **Diagrams** | React Flow | Integration visualizations |
| **Backend** | FastAPI (Python 3.10+) | REST API |
| **AI** | HuggingFace (Qwen 72B) | Document parsing & mapping |
| **Storage** | In-Memory | No database setup needed |

---

## Core Components

### 1️⃣ Document Parser
**File:** `backend/services/document_parser.py`
- Accepts PDF, DOCX, TXT files
- Extracts raw text for AI processing

### 2️⃣ AI Pipeline
**File:** `backend/ai_pipeline/pipeline.py`
- **Extract Requirements** → Parse BRDs using LLM
- **Generate Mappings** → Semantic field matching
- **Create Tests** → Edge case discovery
- **Fallback Logic** → Rule-based backup when AI fails

### 3️⃣ Adapter Registry
**File:** `backend/adapters/registry.py`
- 7 prebuilt adapters (KYC, Payment, GST, Banking)
- Version control for API compatibility
- Easy to extend (15 min per adapter)

### 4️⃣ Simulation Engine
**File:** `backend/services/simulation_engine.py`
- Mock API responses (realistic validation)
- Tests configurations before deployment
- Reports pass/fail with recommendations

---

## AI Usage

| Feature | AI? | Why? |
|---------|-----|------|
| Parse requirements | ✅ Yes | Natural language understanding |
| Map fields | ✅ Yes | Semantic matching (`aadhaar_number` → `aadhaarId`) |
| Generate tests | ✅ Yes | Creative edge cases |
| Run simulations | ❌ No | Rule-based mock APIs |
| Store data | ❌ No | Standard storage |

---

## Data Flow

```
1. UPLOAD    →  User uploads BRD document
2. PARSE     →  AI extracts services & fields (30-60s)
3. GENERATE  →  AI creates field mappings (20-40s)  
4. SIMULATE  →  Mock APIs test the config (2-5s)
5. REVIEW    →  User sees results with confidence scores
```

---

## Key Design Decisions

### ✅ Why HuggingFace (Free Tier)?
- No credit card needed for demos
- Qwen 72B gives good quality
- 1,000 free requests/month

### ✅ Why In-Memory Storage?
- Zero setup for judges
- No database installation
- Easy to extend to PostgreSQL later

### ✅ Why Fallback Logic?
- AI fails ~30% of time (malformed JSON)
- Fallback ensures system never crashes
- Shows production-ready error handling

---

## Security Features

- **Multi-Tenant** → Data isolation per tenant
- **Audit Logs** → Every action tracked
- **Credential Vault** → No hardcoded secrets
- **PII Masking** → Sensitive data protected

---

## File Structure (Key Files)

```
backend/
├── ai_pipeline/
│   ├── pipeline.py      ← AI orchestration + fallback
│   ├── llm_client.py    ← HuggingFace client
│   └── prompts.py       ← Prompt templates
├── adapters/
│   ├── registry.py      ← 7 prebuilt adapters
│   └── mock_apis.py     ← Realistic mock responses
├── services/
│   ├── document_parser.py
│   ├── config_generator.py
│   └── simulation_engine.py
└── main.py              ← FastAPI entry point

frontend/
├── src/
│   ├── pages/           ← Dashboard, Upload, Requirements...
│   └── components/      ← DemoMode, VoiceInput, IntegrationFlow
└── package.json
```

---

## Quick Numbers

| Metric | Value |
|--------|-------|
| Backend Lines | ~2,500 |
| Frontend Lines | ~3,000 |
| API Endpoints | 12 |
| Prebuilt Adapters | 7 |
| Setup Time | 5 minutes |
| Demo Duration | 3 minutes |

---

## Scaling Path (Post-Hackathon)

| Current | Production |
|---------|------------|
| In-Memory | PostgreSQL |
| HuggingFace Free | Dedicated GPU |
| Single Server | Kubernetes |
| Mock APIs | Real integrations |

---

**Built for hackathons. Ready for enterprise.**
