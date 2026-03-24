<div align="center">

# 🛡️ IntelliClaim — Multi-Agent Insurance Claim Validation System

### AI-Powered Claim Processing with LangGraph Agent Orchestration

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

---

**IntelliClaim** is an enterprise-grade, AI-powered insurance claim processing platform that leverages a **multi-agent architecture** to validate, process, and make intelligent decisions on insurance claims. It combines six specialized AI agents orchestrated by **LangGraph**, a **FastAPI** backend, and a polished **React + TypeScript** frontend to deliver end-to-end claim automation.

[Features](#-features) · [Architecture](#-architecture) · [Tech Stack](#-tech-stack) · [Getting Started](#-getting-started) · [API Reference](#-api-reference) · [Project Structure](#-project-structure)

</div>

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [The Six AI Agents](#-the-six-ai-agents)
- [Claim Processing Workflow](#-claim-processing-workflow)
- [Tech Stack](#-tech-stack)
- [Insurance Plans & Coverage](#-insurance-plans--coverage)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Frontend Pages & Flow](#-frontend-pages--flow)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Performance Optimizations](#-performance-optimizations)

---

## ✨ Features

### Core Capabilities
- **Multi-Agent AI Pipeline** — Six specialized agents work in concert to validate claims through identity verification, document analysis, policy checks, fraud detection, and final decision-making
- **LangGraph Orchestration** — Directed acyclic graph (DAG) execution with parallel agent processing and conditional routing
- **Real-Time LLM Chat** — Groq-powered conversational assistant for claim queries with session-based context
- **Cross-Agent Validation** — Automatic cross-referencing of data extracted by different agents to catch inconsistencies
- **Automated Email Reports** — Personalized decision reports generated and sent upon claim completion

### Identity & Document Processing
- **Aadhaar Verification** — OCR extraction + Verhoeff checksum validation of Indian Aadhaar identity cards
- **Document OCR** — OpenCV + Tesseract-based text extraction from PDFs and images with intelligent preprocessing
- **Document Summarization** — LLM-powered summarization of uploaded insurance documents
- **Vector Similarity Search** — FAISS-based document embedding for semantic retrieval (RAG)

### Platform Features
- **JWT Authentication** — Secure OAuth2 password flow with bcrypt-hashed passwords
- **Step-by-Step Claim Wizard** — Guided 7-step frontend flow with progress tracking
- **Responsive Design** — Premium UI built with shadcn/ui, Radix primitives, and Tailwind CSS
- **Drag & Drop Uploads** — File upload with drag support for identity and claim documents
- **Protected Routes** — Role-based access control on all claim operations

---

## 🏗 Architecture

<div align="center">

![IntelliClaim Architecture](documentation/assets/images/architecture.jpg)

*High-level architecture of the IntelliClaim multi-agent system*

</div>

The system follows a **three-tier architecture**:

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| **Frontend** | React 18 + TypeScript + Vite | User interface, claim wizard, chat widget |
| **Backend API** | FastAPI + SQLAlchemy | REST API, authentication, routing, database |
| **Agent Layer** | LangGraph + Groq LLM | AI orchestration, OCR, NLP, fraud detection |

---

## 🤖 The Six AI Agents

IntelliClaim's intelligence is distributed across six specialized agents, each with a single responsibility:

### 1. 🆔 Identity Verification Agent
> `backend/agents/identity_agent.py`

Validates the claimant's identity through Aadhaar card analysis.

- **OCR Extraction** — Extracts text, name, and age from uploaded Aadhaar card images
- **Verhoeff Checksum** — Validates the 12-digit Aadhaar number using the Verhoeff algorithm
- **Format Validation** — Matches Aadhaar `XXXX XXXX XXXX` regex pattern
- **Data Extraction** — Pulls name and age for downstream cross-validation

### 2. 📄 Document Validation Agent
> `backend/agents/document_agent.py`

Processes and analyzes supporting insurance documents.

- **Multi-Format OCR** — Handles PDFs and images with parallel page-level extraction
- **LLM Summarization** — Generates concise summaries using Groq (llama-3.1-8b-instant)
- **Name & Age Extraction** — Extracts claimant metadata from document text
- **OCR Caching** — Hash-based cache (limit: 100 entries) to avoid redundant processing
- **Vector Embeddings** — FAISS-powered similarity search for document retrieval

### 3. 📋 Policy Eligibility Agent
> `backend/agents/policy_agent.py`

Determines whether the claim is covered under the claimant's active policy.

- **Policy Lookup** — Queries the database for policies linked to the Aadhaar number
- **Expiry Validation** — Ensures the policy is active at the time of claim
- **Coverage Evaluation** — Checks claim amount against plan-specific limits and co-pay percentages
- **Waiting Period Check** — Validates compliance with event-specific waiting periods
- **Plan Details** — Returns detailed coverage information (max amounts, co-pay, covered events)

### 4. 🔍 Fraud Detection Agent
> `backend/agents/fraud_agent.py`

Analyzes claim data for potential fraud indicators.

- **High-Value Flagging** — Flags claims exceeding ₹300,000 for additional scrutiny
- **Cross-Validation** — Compares identity, document, and claim form data
- **Name Similarity** — Uses a 75% match threshold for name verification across sources
- **Age Discrepancy** — Detects age mismatches with ±1 year tolerance
- **Inconsistency Scoring** — Computes a fraud confidence score based on detected anomalies

### 5. 🧠 Master Decision Agent
> `backend/agents/master_agent.py`

Makes the final claim decision by aggregating all agent outputs.

- **Rule-Based Logic** — Deterministic decision engine combining all agent results
- **Three Outcomes** — `APPROVED`, `REJECTED`, or `HUMAN_REVIEW`
- **Confidence Scoring** — Weighted confidence based on individual agent scores
- **Decision Reasoning** — Generates human-readable explanations for each decision
- **Email Report Generation** — Creates detailed personalized reports for claimants

### 6. 💬 Chat Agent
> `backend/agents/chat_agent.py`

Provides an AI-powered conversational interface for claim inquiries.

- **Contextual Responses** — Accesses claim state to provide relevant answers
- **Session Management** — Maintains chat history (last 6 messages) per session
- **Groq LLM Backend** — Fast responses using llama-3.1-8b-instant
- **30-Minute Sessions** — Automatic session expiry for security
- **Context Truncation** — Limits context to 2,000 characters for optimal LLM performance

---

## 🔄 Claim Processing Workflow

The claim graph is built using **LangGraph's StateGraph** and executes agents in the following topology:

```
                    ┌──────────────┐
                    │   Identity   │
                    │    Agent     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
       ┌────────────┐ ┌─────────┐ ┌──────────┐
       │  Document   │ │ Policy  │ │  Fraud   │
       │   Agent     │ │  Agent  │ │  Agent   │
       └──────┬──────┘ └────┬────┘ └────┬─────┘
              │             │           │
              └─────────────┼───────────┘
                            │
                     ┌──────▼───────┐
                     │   Master     │
                     │  Decision    │
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │   Notify     │
                     │  (Email)     │
                     └──────────────┘
```

**Key characteristics:**
- The **Identity Agent** executes first as the entry point
- **Document, Policy, and Fraud agents** run in parallel after identity verification
- All three feed into the **Master Decision Agent** for final adjudication
- The **Notification service** sends the email report as the final step

---

## 🧰 Tech Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | Async REST API with automatic OpenAPI docs |
| **Agent Orchestration** | LangGraph | DAG-based multi-agent workflow execution |
| **LLM Provider** | Groq (llama-3.1-8b-instant) | Document summarization, chat responses |
| **NLP Framework** | LangChain | Chain composition, embedding models |
| **OCR Engine** | Tesseract + OpenCV | Text extraction from images and PDFs |
| **PDF Processing** | pdf2image + Pillow | PDF to image conversion for OCR |
| **Vector Store** | FAISS (CPU) | Semantic similarity search for RAG |
| **Database ORM** | SQLAlchemy | Data models and query builder |
| **Database** | PostgreSQL / SQLite | Persistent storage (Postgres for prod, SQLite for dev) |
| **Authentication** | python-jose + passlib + bcrypt | JWT tokens, OAuth2, password hashing |
| **Validation** | Pydantic | Request/response schema validation |
| **Server** | Uvicorn | ASGI server |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | React 18 | Component-based UI |
| **Language** | TypeScript | Type-safe development |
| **Build Tool** | Vite | Lightning-fast dev server and builds |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **UI Components** | shadcn/ui + Radix UI | Accessible, headless component primitives |
| **Routing** | React Router v6 | Client-side routing with protected routes |
| **Forms** | React Hook Form + Zod | Form state management and schema validation |
| **Data Fetching** | TanStack React Query | Server state management with caching |
| **Charts** | Recharts | Data visualization on the dashboard |
| **Icons** | Lucide React | Consistent icon system |
| **Notifications** | Sonner | Toast notifications |
| **Testing** | Vitest + Testing Library | Unit and component testing |

---

## 💎 Insurance Plans & Coverage

IntelliClaim supports three tiered insurance plans:

| Feature | 🥈 Shield Silver | 🥇 Shield Gold | 💎 Shield Platinum |
|---------|:-----------------:|:---------------:|:-------------------:|
| **Max Coverage** | ₹3,00,000 | ₹50,00,000 | ₹1,00,00,000 |
| **Motor** | ✅ ₹1.5L (10% co-pay) | ✅ ₹25L (5% co-pay) | ✅ ₹50L (2% co-pay) |
| **Health** | ✅ ₹3L (0% co-pay) | ✅ ₹50L (0% co-pay) | ✅ ₹1Cr (0% co-pay) |
| **Home** | ❌ | ✅ ₹20L (5% co-pay) | ✅ ₹50L (5% co-pay) |
| **Travel** | ❌ | ✅ ₹10L (10% co-pay) | ✅ ₹25L (5% co-pay) |
| **Life** | ❌ | ❌ | ✅ ₹1Cr (0% co-pay) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (or Bun)
- **Tesseract OCR** installed and available in PATH
- **Poppler** (for PDF to image conversion)
- **Groq API Key** ([Get one here](https://console.groq.com/))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/multiagent_insurance_claim_validation.git
cd multiagent_insurance_claim_validation
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration (see Environment Variables below)

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or: bun install

# Start the development server
npm run dev
# or: bun dev
```

The frontend will be available at `http://localhost:5000` and the backend API at `http://localhost:8000`.

### 4. Docker (Backend Only)

```bash
cd backend
docker build -t intelliclaim-backend .
docker run -p 8000:8000 --env-file .env intelliclaim-backend
```

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./intelliclaim.db    # SQLite for dev
# DATABASE_URL=postgresql://user:pass@host:5432/intelliclaim  # Postgres for prod

# LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# JWT Authentication
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5000
```

For the frontend, create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/token` | Login and get JWT token |
| `GET` | `/auth/me` | Get current user info |

### Identity Verification

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/identity/create-claim` | Create a new claim and begin identity verification |
| `POST` | `/identity/extract-aadhaar` | Extract and validate Aadhaar from uploaded image |

### Policy

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/policy/check` | Check policy eligibility for a claim |

### Documents

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/documents/upload-and-validate` | Upload and validate insurance documents |
| `POST` | `/documents/extract-name-age` | Extract claimant name and age from documents |

### Fraud Detection

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/fraud/cross-validate/{claim_id}` | Run cross-agent fraud validation |

### Chat

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/chat/init` | Initialize a new chat session |
| `POST` | `/chat/message` | Send a message and get AI response |

### Master Decision

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/master/send-report` | Generate and send the decision report |
| `GET` | `/master/claim-summary` | Get the complete claim summary |

### Claim Types

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/claims/motor` | Submit motor insurance claim details |
| `POST` | `/claims/health` | Submit health insurance claim details |

### Health

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/health/` | API health check |

> 📘 **Interactive API docs** are available at `http://localhost:8000/docs` (Swagger UI) after starting the backend.

---

## 🖥 Frontend Pages & Flow

The frontend guides users through a **7-step claim submission wizard**:

```
┌─────────┐    ┌───────────┐    ┌────────────┐    ┌──────────────┐
│  Login   │───▶│ Dashboard │───▶│ Claim Type │───▶│Claim Details │
│  /auth   │    │/dashboard │    │/claim/type │    │/claim/details│
└─────────┘    └───────────┘    └────────────┘    └──────┬───────┘
                                                         │
┌───────────────┐    ┌──────────────┐    ┌───────────────▼──────┐
│  Processing   │◀───│  Documents   │◀───│  Aadhaar Verify      │
│/claim/process │    │/claim/docs   │    │  /claim/id-verify    │
└───────────────┘    └──────────────┘    └──────────────────────┘
```

| Step | Page | Description |
|------|------|-------------|
| **1** | **Auth** | Login or sign up with email and password |
| **2** | **Dashboard** | Overview with recent claims, stats, and quick actions |
| **3** | **Claim Start** | Select claimant type — Individual or Company |
| **4** | **Claim Type** | Choose insurance category — Health, Vehicle, Property, or Life |
| **5** | **Claim Details** | Fill type-specific claim information (amount, date, description) |
| **6** | **Aadhaar Verify** | Upload Aadhaar card for identity verification |
| **7** | **Claim Narrative** | Describe the incident in your own words |
| **8** | **Documents** | Upload supporting documents (medical reports, FIRs, invoices) |
| **9** | **Processing** | View AI agent results and final decision |

### Key UI Features
- **Progress Bar** — Visual step indicator showing completed, current, and upcoming steps
- **Chat Widget** — Floating AI assistant available throughout the claim flow
- **Protected Routes** — Unauthenticated users are redirected to login
- **Persistent State** — Claim progress saved in `localStorage` to survive page refreshes
- **Responsive Layout** — Fully responsive design across mobile, tablet, and desktop

---

## 📁 Project Structure

```
multiagent_insurance_claim_validation/
│
├── 📂 backend/                          # FastAPI Backend
│   ├── main.py                          # App entry point, CORS, route registration
│   ├── state.py                         # ClaimState, AgentResult, CrossValidation types
│   ├── Dockerfile                       # Docker container configuration
│   ├── requirements.txt                 # Python dependencies
│   │
│   ├── 📂 agents/                       # AI Agent implementations
│   │   ├── identity_agent.py            # Aadhaar identity verification
│   │   ├── document_agent.py            # Document OCR, summarization & validation
│   │   ├── policy_agent.py              # Policy eligibility evaluation
│   │   ├── fraud_agent.py               # Fraud detection & cross-validation
│   │   ├── master_agent.py              # Final decision aggregation
│   │   └── chat_agent.py               # LLM-powered chat assistant
│   │
│   ├── 📂 api/routes/                   # REST API endpoints
│   │   ├── auth.py                      # Authentication (signup, login, me)
│   │   ├── identity.py                  # Identity verification endpoints
│   │   ├── policy.py                    # Policy check endpoints
│   │   ├── documents.py                 # Document upload & extraction
│   │   ├── fraud.py                     # Fraud cross-validation
│   │   ├── chat.py                      # Chat session management
│   │   ├── master.py                    # Decision report & summary
│   │   ├── basic.py                     # Claim type endpoints (motor, health)
│   │   └── health.py                    # Health check endpoint
│   │
│   ├── 📂 auth/                         # Authentication & security
│   │   ├── jwt_handler.py               # JWT token creation & verification
│   │   ├── oauth2.py                    # OAuth2 password flow
│   │   └── security.py                  # Password hashing utilities
│   │
│   ├── 📂 db/                           # Database configuration
│   │   ├── base.py                      # SQLAlchemy declarative base
│   │   └── session.py                   # Engine & session factory
│   │
│   ├── 📂 models/                       # SQLAlchemy ORM models
│   │   ├── user.py                      # User model (auth)
│   │   └── policy.py                    # Policy model (Aadhaar → policy mapping)
│   │
│   ├── 📂 schemas/                      # Pydantic schemas
│   │   ├── auth.py                      # Auth request/response schemas
│   │   ├── agent.py                     # Agent result schemas
│   │   ├── chat.py                      # Chat message schemas
│   │   ├── decision.py                  # Decision response schemas
│   │   └── policy.py                    # Policy check schemas
│   │
│   ├── 📂 graph/                        # LangGraph workflow
│   │   └── claim_graph.py              # StateGraph DAG definition
│   │
│   ├── 📂 documents/                    # Document processing utilities
│   │   ├── ocr.py                       # OpenCV + Tesseract OCR pipeline
│   │   ├── pdf_utils.py                 # PDF to image conversion
│   │   ├── embeddings.py               # FAISS vector store & embeddings
│   │   ├── rag.py                       # Retrieval-augmented generation
│   │   └── validation.py               # Document validation logic
│   │
│   ├── 📂 identity/                     # Identity processing
│   │   ├── aadhar_validator.py          # Verhoeff checksum validation
│   │   ├── classifier.py               # Document type classification
│   │   ├── image_utils.py              # Image preprocessing
│   │   └── ocr_utils.py                # Identity-specific OCR
│   │
│   ├── 📂 policy/                       # Policy logic
│   │   ├── plan_definitions.py          # Silver/Gold/Platinum plan configs
│   │   └── eligibility.py              # Coverage & eligibility evaluation
│   │
│   └── 📂 services/                     # External services
│       ├── claim_store.py               # In-memory claim state management
│       └── notifications.py            # Email notification service
│
├── 📂 frontend/                         # React Frontend
│   ├── index.html                       # HTML entry point
│   ├── package.json                     # Node.js dependencies
│   ├── vite.config.ts                   # Vite configuration
│   ├── tailwind.config.ts               # Tailwind CSS configuration
│   ├── tsconfig.json                    # TypeScript configuration
│   │
│   └── 📂 src/
│       ├── App.tsx                      # Root component with routing
│       ├── main.tsx                     # React DOM entry point
│       │
│       ├── 📂 pages/                    # Page components
│       │   ├── Auth.tsx                 # Login / Signup page
│       │   ├── Dashboard.tsx            # User dashboard
│       │   ├── ClaimStart.tsx           # Claimant type selection
│       │   ├── ClaimType.tsx            # Insurance type selection
│       │   ├── ClaimDetails.tsx         # Claim details form
│       │   ├── ClaimAadhar.tsx          # Aadhaar upload & verification
│       │   ├── ClaimNarrative.tsx       # Incident narrative
│       │   ├── ClaimDocuments.tsx       # Document upload
│       │   └── ClaimProcessing.tsx      # Results & decision display
│       │
│       ├── 📂 components/               # Reusable components
│       │   ├── ChatAssistant.tsx        # Floating AI chat widget
│       │   ├── ClaimLayout.tsx          # Shared claim wizard layout
│       │   ├── NavLink.tsx              # Navigation components
│       │   └── 📂 ui/                   # 40+ shadcn/ui components
│       │
│       ├── 📂 contexts/                 # React Context providers
│       │   ├── AuthContext.tsx           # Authentication state
│       │   └── ClaimContext.tsx          # Claim workflow state
│       │
│       ├── 📂 hooks/                    # Custom React hooks
│       │   ├── use-mobile.tsx           # Mobile breakpoint detection
│       │   └── use-toast.ts             # Toast notification hook
│       │
│       └── 📂 lib/                      # Utility functions
│           ├── utils.ts                 # General utilities
│           └── terminalLog.ts           # Developer logging
│
└── 📂 documentation/                    # Project documentation
    └── 📂 assets/images/               # Architecture diagrams
```

---

## 🔒 Security

### Implemented
- ✅ **JWT Authentication** — Stateless token-based auth with configurable expiry
- ✅ **Bcrypt Password Hashing** — Industry-standard salted password hashing
- ✅ **OAuth2 Password Flow** — Standards-compliant authentication flow
- ✅ **CORS Protection** — Whitelisted origins only
- ✅ **Protected Routes** — Frontend and backend route guards
- ✅ **Session Expiry** — Chat sessions auto-expire after 30 minutes
- ✅ **Input Validation** — Pydantic schemas validate all API inputs

### Recommendations for Production
- 🔧 Move secret keys to environment variables / secrets manager
- 🔧 Add rate limiting on authentication endpoints
- 🔧 Implement audit logging for all claim operations
- 🔧 Add HTTPS enforcement
- 🔧 Move session store from in-memory to Redis
- 🔧 Add CSRF protection for cookie-based sessions

---

## ⚡ Performance Optimizations

| Optimization | Description |
|-------------|-------------|
| **OCR Caching** | Hash-based cache (100 entries max) prevents redundant OCR on the same documents |
| **Parallel OCR** | Multi-threaded extraction (2 workers) for multi-page documents |
| **Vector Store Cache** | FAISS index caching (50 entries max) for repeated similarity queries |
| **Lazy Imports** | Heavy libraries (OpenCV, Tesseract, LangChain) loaded on demand |
| **Context Truncation** | LLM context trimmed to 2,000 characters for faster inference |
| **Singleton Embeddings** | Single embedding model instance shared across requests |
| **Parallel Agents** | Document, Policy, and Fraud agents run concurrently in the graph |
| **Optimized Image Scaling** | 1.5x scaling for OCR preprocessing (balanced quality vs. speed) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">



</div>
