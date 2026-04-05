# 🎤 Demo Script - Detailed Version

## Pre-Demo Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Browser open to http://localhost:3000
- [ ] `demo_data/sample_brd.txt` ready for upload
- [ ] Terminal visible for backend logs (optional but impressive)

## Demo Flow (5-7 minutes)

### 🎬 Scene 1: The Problem (30 seconds)

**Say:**
> "Every enterprise has dozens of integrations - KYC providers, payment gateways, GST systems. 
> Setting up each integration takes weeks of developer time. Why?
> - Reading 50-page requirement documents
> - Manually mapping fields between systems
> - Writing transformation code
> - Testing against each API
> 
> What if AI could do this in minutes?"

**Do:** Show the Dashboard with empty stats (fresh state)

---

### 🎬 Scene 2: Document Upload (45 seconds)

**Navigate to:** Upload page

**Say:**
> "Let's start with a real Business Requirements Document. This is a 4-page BRD for a customer onboarding platform."

**Do:**
1. Drag and drop `sample_brd.txt` into the upload zone
2. Show the preview appears
3. Point out the document type selector (BRD, SOW, API Spec)

**Say:**
> "The system accepts PDFs, Word docs, or plain text. Let's see what AI extracts."

**Do:** Click "Extract Requirements with AI"

**Say while loading:**
> "The AI is reading the entire document, understanding the context, and extracting structured requirements."

---

### 🎬 Scene 3: Review Extracted Requirements (1 minute)

**Page:** Requirements detail view

**Say:**
> "Look at this! From a 4-page document, AI extracted 6 distinct services."

**Do:** Point to each service card

**Say:**
> "It identified:
> - Aadhaar KYC - marked as MANDATORY
> - PAN Verification - MANDATORY
> - Payment Gateway - MANDATORY
> - UPI Integration - OPTIONAL
> - GST Verification - OPTIONAL
> - Bank Account - CONDITIONAL
>
> Notice the priority classification. The AI understood words like 'must', 'required', 'optional' from natural language."

**Do:** Expand one service (Aadhaar KYC)

**Say:**
> "For each service, it extracted:
> - Required fields (aadhaar_number, full_name, mobile)
> - Optional fields (email, address)
> - Constraints like '30 second timeout' and 'OTP expires in 10 minutes'
>
> This is the confidence score - 92%. High confidence means the AI found explicit mentions."

**Do:** Scroll to show security and compliance sections

**Say:**
> "It even extracted security requirements like 'AES-256 encryption' and compliance like 'RBI KYC guidelines'."

---

### 🎬 Scene 4: Generate Configuration (1 minute)

**Do:** Click "Generate Configuration"

**Say:**
> "Now watch the magic. The AI is:
> 1. Finding the right adapters from our registry
> 2. Mapping source fields to target fields
> 3. Generating transformation rules
> 4. Creating the complete configuration"

**Page:** Configuration detail view

**Do:** Show the field mappings table

**Say:**
> "Look at this mapping. The source field 'aadhaar_number' maps to 'aadhaarId' in the target API.
> The AI added a transformation: `trim() | validate_aadhaar()` - it knows Aadhaar needs validation.
>
> For dates, it converts from 'YYYY-MM-DD' to 'DD/MM/YYYY' - the format the target API expects."

**Do:** Click on JSON tab briefly

**Say:**
> "The complete configuration is production-ready JSON. Error handling, retry logic, circuit breakers - all configured."

**Do:** Show Validation tab

**Say:**
> "The AI also validated the configuration - 92% score. One warning: 'Consider reducing timeout for better UX.'"

---

### 🎬 Scene 5: Run Simulation (1 minute)

**Navigate to:** Simulation page

**Say:**
> "Before deploying to production, let's test this configuration against mock APIs."

**Do:** Select the configuration and click "Run Simulation"

**Say:**
> "The simulation is running test scenarios - happy paths, error cases, edge cases."

**Do:** Show results when complete

**Say:**
> "8 tests, 7 passed, 1 failed. 87.5% pass rate.
>
> Let's look at the failed test - 'Network Timeout'. The mock API returned 503.
> 
> The system recommends: 'Add retry logic for transient failures.'"

**Do:** Scroll to show detailed test results

**Say:**
> "Every test shows the input sent, expected response, and actual response. Complete visibility."

---

### 🎬 Scene 6: Enterprise Features (45 seconds)

**Do:** Show the Adapters page

**Say:**
> "We have a registry of pre-built adapters - KYC, Payment, GST, Banking. Each adapter knows the target schema."

**Do:** Expand one adapter to show endpoints and schema

**Say:**
> "Adding new integrations is just adding a new adapter definition. The AI handles the mapping."

**Navigate to:** Configurations page, show version dropdown (if you have multiple)

**Say:**
> "Every configuration is versioned. If something goes wrong in production, one-click rollback.
> 
> There's also full audit logging - who changed what, when. Compliance ready."

---

### 🎬 Scene 7: Closing (30 seconds)

**Say:**
> "Let's recap what just happened:
> - We uploaded a 4-page requirement document
> - AI extracted 6 services, dozens of fields, all constraints
> - Generated complete integration configurations
> - Tested against 8 scenarios
> 
> Total time: 3 minutes. Without AI, this takes 2-3 weeks.
>
> That's SyncBridge AI - from requirements to production-ready configs in minutes.
>
> Questions?"

---

## 🎯 Anticipated Questions & Answers

### "How is AI actually used here?"

> "Great question! AI is used for three specific things:
> 1. **Document Understanding** - Reading natural language and extracting structured data. Rules can't handle 'must implement Aadhaar verification' being phrased ten different ways.
> 2. **Semantic Field Mapping** - Understanding that 'phone_number', 'mobile', and 'contact' all mean the same thing.
> 3. **Context-Aware Validation** - Knowing that PII fields need encryption based on industry context.
>
> We have clear prompt engineering - I can show you the prompts in the code."

### "What if the AI makes mistakes?"

> "Three safeguards:
> 1. **Confidence Scores** - If AI is uncertain, it flags it for human review
> 2. **Simulation Testing** - Every config is tested before deployment
> 3. **Fallback Logic** - If AI fails, we have rule-based extraction as backup
>
> The human is always in the loop before production."

### "Is this just a demo or production-ready?"

> "It's production-architected:
> - Multi-tenant from day one
> - Full audit logging for compliance
> - Version control with rollback
> - Credential vault (mock implementation, but the pattern is there)
> - Error handling and circuit breakers
>
> In a real deployment, you'd add a database and real API keys."

### "How long did this take to build?"

> "This is a hackathon prototype built in 48 hours. The core architecture - API, AI pipeline, adapter pattern - is solid. For production, you'd add:
> - Persistent database
> - Real authentication
> - More adapters
> - Monitoring and alerting"

### "Can it handle complex nested documents?"

> "Yes! The AI processes the full document context. For very large documents, we chunk and process sections. The current limit is about 15,000 characters, but that covers most BRDs."

---

## 🔥 Pro Tips

1. **Keep terminal visible** - Backend logs showing "Generating mappings via LLM" adds credibility
2. **Use real document** - The sample BRD is realistic, not toy data
3. **Show the code briefly** - "Here's the prompt that does extraction" - judges love transparency
4. **Time your demo** - Practice to hit exactly 5 minutes, leave time for questions
5. **Have backups** - Export sample JSONs in case API is slow
