<div align="center">

<img src="https://img.shields.io/badge/version-0.1.0--beta-534AB7?style=flat-square" alt="version" />
<img src="https://img.shields.io/badge/license-MIT-1D9E75?style=flat-square" alt="license" />
<img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="python" />
<img src="https://img.shields.io/badge/react-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="react" />
<img src="https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="docker" />
<img src="https://img.shields.io/badge/status-in%20development-BA7517?style=flat-square" alt="status" />

<br />
<br />

```
███╗   ███╗██╗   ██╗██╗  ████████╗██╗███╗   ███╗███████╗██████╗  █████╗ ██╗
████╗ ████║██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔════╝██╔══██╗██╔══██╗██║
██╔████╔██║██║   ██║██║     ██║   ██║██╔████╔██║█████╗  ██║  ██║███████║██║
██║╚██╔╝██║██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══╝  ██║  ██║██╔══██║██║
██║ ╚═╝ ██║╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║███████╗██████╔╝██║  ██║██║
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝
```

**Multimodal AI-powered preliminary health risk assessment platform**

*Combining computer vision, NLP, OCR, and physiological data into a single unified analysis report*

<br />

[Getting Started](#-getting-started) · [Architecture](#-architecture) · [API Reference](#-api-reference) · [AI Modules](#-ai-modules) · [Contributing](#-contributing) · [Disclaimer](#-medical-disclaimer)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [AI Modules](#-ai-modules)
- [API Reference](#-api-reference)
- [Frontend Screens](#-frontend-screens)
- [Database Schema](#-database-schema)
- [Async Pipeline](#-async-pipeline)
- [Development Guide](#-development-guide)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Medical Disclaimer](#-medical-disclaimer)

---

## 🧠 Overview

**MultiMedAI** is a multimodal health risk assessment platform that aggregates information from four distinct input sources — medical images, symptom descriptions, PDF documents, and wearable sensor data — and fuses them through a weighted AI pipeline to produce a structured, human-readable risk report.

The platform is designed as a **preliminary analysis aid**, not a diagnostic tool. It helps users organize and contextualize their health information before a medical consultation, and provides a conversational AI assistant that can answer questions grounded in the generated report.

> **Context:** This project was developed as a Final Year Project (PFE — Projet de Fin d'Études) to demonstrate applied skills in computer vision, NLP, document processing, full-stack development, and multimodal AI fusion.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Image Analysis** | YOLOv11 detects skin lesions, wounds, redness, swelling, and other visual anomalies |
| **Symptom NLP** | Local LLM (Llama 3.1) extracts symptoms, duration, severity, and urgency signals |
| **PDF/OCR Processing** | PaddleOCR extracts text from medical reports; LLM identifies medications and lab values |
| **Sensor Integration** | Rule-based scoring on SpO₂, temperature, heart rate, and sleep data |
| **Multimodal Fusion** | Weighted fusion algorithm combines all modality scores into a single risk level |
| **Risk Gauge** | Three-level output: `Normal` · `Surveiller` · `Consultation urgente` |
| **Chat Assistant** | RAG-powered assistant answers questions grounded in the user's own report |
| **PDF Export** | Downloadable report suitable for sharing with a healthcare professional |
| **Real-time Progress** | Live analysis status with per-module progress tracking |
| **Fully Dockerized** | One-command local setup with all services containerized |

---

## 🛠 Tech Stack

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript |
| Build tool | Vite |
| Styling | TailwindCSS + shadcn/ui |
| Server state | React Query (TanStack Query v5) |
| Client state | Zustand |
| Routing | React Router v6 |
| HTTP client | Axios |

### Backend
| Layer | Technology |
|---|---|
| API framework | FastAPI (Python 3.11) |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Task queue | Celery + Redis |
| File storage | MinIO (S3-compatible) |

### AI / ML
| Module | Technology |
|---|---|
| Image detection | YOLOv11 (ultralytics) |
| OCR | PaddleOCR |
| LLM inference | Ollama + Llama 3.1 8B |
| LLM orchestration | LangChain |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector store | Qdrant |

### Infrastructure
| Component | Technology |
|---|---|
| Database | PostgreSQL 15 + pgvector |
| Cache / Broker | Redis 7 |
| Reverse proxy | Nginx |
| Containerization | Docker + Docker Compose |
| PDF export | WeasyPrint |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                     React 18 + TypeScript                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP / SSE
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Nginx (port 80)                          │
│                       Reverse Proxy                             │
└──────────┬──────────────────────────────────────────────────────┘
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
┌─────────┐  ┌─────────────────────────────────────────────────┐
│ Static  │  │             FastAPI (port 8000)                  │
│ Assets  │  │                                                  │
│ (React) │  │  /api/v1/analysis   →  Analysis Router           │
└─────────┘  │  /api/v1/report     →  Report Router             │
             │  /api/v1/chat       →  Chat Router (SSE)         │
             └───────────┬─────────────────────────────────────┘
                         │
           ┌─────────────┼────────────────────┐
           │             │                    │
           ▼             ▼                    ▼
    ┌─────────────┐ ┌─────────┐       ┌──────────────┐
    │  PostgreSQL │ │  Redis  │       │    MinIO     │
    │  + pgvector │ │(broker) │       │(file storage)│
    └─────────────┘ └────┬────┘       └──────────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │    Celery Worker      │
             │                       │
             │  ┌─────────────────┐  │
             │  │  YOLO Service   │  │  ← YOLOv11 inference
             │  ├─────────────────┤  │
             │  │  LLM  Service   │  │  ← Ollama / Llama 3.1
             │  ├─────────────────┤  │
             │  │  OCR  Service   │  │  ← PaddleOCR
             │  ├─────────────────┤  │
             │  │ Sensor Service  │  │  ← Rule-based scoring
             │  ├─────────────────┤  │
             │  │ Fusion Service  │  │  ← Weighted aggregation
             │  └─────────────────┘  │
             └───────────┬───────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   Qdrant    │
                  │(vector DB)  │  ← RAG embeddings
                  └─────────────┘
```

### Fusion Logic

Each modality produces a `risk_score` in `[0.0, 1.0]`. The global score is computed as a **weighted average over active modalities only** — missing inputs have their weight redistributed proportionally.

```
global_score = Σ(weight_i × score_i) / Σ(weight_i)   [active modalities only]

Default weights:   image=0.35  ·  text=0.30  ·  pdf=0.20  ·  sensor=0.15

Risk thresholds:   0.00 – 0.35  →  Normal
                   0.35 – 0.65  →  Surveiller
                   0.65 – 1.00  →  Consultation urgente
```

---

## 📁 Project Structure

```
multimedai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, router registration
│   │   ├── config.py                # Pydantic settings from .env
│   │   ├── database.py              # Async SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── analysis.py          # Analysis, ModalityResult ORM models
│   │   │   ├── report.py            # Report, ChatMessage ORM models
│   │   │   └── user.py              # User model (optional auth)
│   │   ├── schemas/
│   │   │   ├── analysis.py          # Request/response Pydantic schemas
│   │   │   ├── report.py            # Report and modality schemas
│   │   │   └── chat.py              # Chat message schemas
│   │   ├── routers/
│   │   │   ├── analysis.py          # POST /analysis, GET /analysis/{id}/status
│   │   │   ├── report.py            # GET /report/{id}, GET /report/{id}/pdf
│   │   │   └── chat.py              # POST /chat  (SSE streaming)
│   │   ├── services/
│   │   │   ├── yolo_service.py      # YOLOv11 image inference
│   │   │   ├── llm_service.py       # Ollama/OpenAI LLM calls
│   │   │   ├── ocr_service.py       # PaddleOCR + pdf2image pipeline
│   │   │   ├── sensor_service.py    # Physiological data scoring
│   │   │   ├── fusion_service.py    # Weighted multimodal fusion
│   │   │   ├── report_service.py    # Report generation + formatting
│   │   │   └── chat_service.py      # RAG chain + SSE streaming
│   │   ├── tasks/
│   │   │   └── analysis_tasks.py    # Celery async task definitions
│   │   └── utils/
│   │       ├── file_handler.py      # MinIO upload/download helpers
│   │       └── pdf_export.py        # WeasyPrint PDF generation
│   ├── alembic/                     # Database migrations
│   ├── tests/
│   │   ├── test_yolo.py
│   │   ├── test_llm.py
│   │   ├── test_fusion.py
│   │   └── test_api.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── InputPage.tsx        # Screen 1 — upload + symptoms
│   │   │   ├── AnalysisPage.tsx     # Screen 2 — real-time progress
│   │   │   ├── ReportPage.tsx       # Screen 3 — structured report
│   │   │   └── ChatPage.tsx         # Screen 4 — contextual assistant
│   │   ├── components/
│   │   │   ├── UploadZone.tsx       # Drag-and-drop file upload
│   │   │   ├── SymptomInput.tsx     # Tag-based symptom input
│   │   │   ├── SensorPanel.tsx      # Wearable data display
│   │   │   ├── RiskGauge.tsx        # Animated tricolor gauge (signature)
│   │   │   ├── ModalityCard.tsx     # Per-modality result card
│   │   │   ├── AnalysisStage.tsx    # Progress checklist item
│   │   │   └── ChatBubble.tsx       # Message bubble component
│   │   ├── store/
│   │   │   └── analysisStore.ts     # Zustand global state
│   │   ├── api/
│   │   │   ├── client.ts            # Axios instance + interceptors
│   │   │   └── hooks.ts             # React Query custom hooks
│   │   └── types/
│   │       └── index.ts             # Shared TypeScript interfaces
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml
├── docker-compose.override.yml      # Local dev overrides
├── nginx.conf
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 24+ and [Docker Compose](https://docs.docker.com/compose/) v2
- [Git](https://git-scm.com/)
- 8 GB RAM minimum (16 GB recommended if running Ollama locally)
- Optional: NVIDIA GPU with CUDA for faster YOLO inference

### 1. Clone the repository

```bash
git clone https://github.com/your-username/multimedai.git
cd multimedai
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values — see [Configuration](#-configuration) for details.

### 3. Pull the LLM model (Ollama)

```bash
# This runs inside the ollama container once it starts
docker compose run --rm ollama ollama pull llama3.1:8b
```

### 4. Start all services

```bash
docker compose up --build
```

This starts 9 services: `frontend`, `backend`, `worker`, `postgres`, `redis`, `minio`, `qdrant`, `ollama`, `nginx`.

### 5. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 6. Access the application

| Service | URL |
|---|---|
| **Application** | http://localhost |
| **API docs (Swagger)** | http://localhost/api/v1/docs |
| **MinIO console** | http://localhost:9001 |
| **Qdrant dashboard** | http://localhost:6333/dashboard |
| **Flower (Celery monitor)** | http://localhost:5555 |

---

## ⚙️ Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and fill in the required values.

```env
# ── Application ────────────────────────────────────────────────
APP_ENV=development                       # development | production
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost,http://localhost:3000

# ── PostgreSQL ──────────────────────────────────────────────────
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=multimedai
POSTGRES_USER=multimedai
POSTGRES_PASSWORD=changeme

# ── Redis ───────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── MinIO ───────────────────────────────────────────────────────
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_IMAGES=multimedai-images
MINIO_BUCKET_DOCUMENTS=multimedai-documents
MINIO_SECURE=false

# ── Qdrant ──────────────────────────────────────────────────────
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=multimedai_reports

# ── LLM ─────────────────────────────────────────────────────────
LLM_PROVIDER=ollama                       # ollama | openai
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b
OPENAI_API_KEY=                           # Required if LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# ── YOLO ────────────────────────────────────────────────────────
YOLO_MODEL_PATH=./models/yolov11n.pt
YOLO_CONFIDENCE_THRESHOLD=0.40

# ── Fusion weights ──────────────────────────────────────────────
FUSION_WEIGHT_IMAGE=0.35
FUSION_WEIGHT_TEXT=0.30
FUSION_WEIGHT_PDF=0.20
FUSION_WEIGHT_SENSOR=0.15

# ── Risk thresholds ─────────────────────────────────────────────
RISK_THRESHOLD_NORMAL=0.35
RISK_THRESHOLD_WARN=0.65
```

---

## 🤖 AI Modules

### Module 1 — Image Detection (YOLOv11)

Accepts a JPEG/PNG image and runs object detection to identify visible medical anomalies.

**Detected classes:** `lesion` · `wound` · `redness` · `swelling` · `ulcer` · `normal_skin`

**Output schema:**
```json
{
  "detections": [
    {
      "label": "lesion",
      "confidence": 0.78,
      "bbox": [x1, y1, x2, y2],
      "area_cm2": 2.1
    }
  ],
  "risk_score": 0.78,
  "summary": "Skin lesion detected on upper left arm with 78% confidence."
}
```

**Model:** YOLOv11n fine-tuned on the [ISIC 2019 dataset](https://challenge.isic-archive.com/data/#2019). Fallback: YOLOv8n with COCO weights.

---

### Module 2 — Symptom Analysis (LLM)

Processes free-text symptom descriptions and extracts structured clinical information.

**System prompt excerpt:**
```
You are a medical NLP extractor. Given a patient's symptom description,
extract a structured JSON object. Never provide a diagnosis.
Output ONLY valid JSON, no prose.
```

**Output schema:**
```json
{
  "symptoms": [
    { "name": "fever", "duration": "3 days", "severity": 6 },
    { "name": "dry cough", "duration": "2 days", "severity": 4 }
  ],
  "risk_keywords": ["persistent fever", "fatigue"],
  "urgency_signals": [],
  "risk_score": 0.52,
  "summary": "Patient reports 3-day fever with dry cough and fatigue."
}
```

---

### Module 3 — Document OCR (PaddleOCR)

Extracts text from PDF medical documents, then passes it to the LLM for structured parsing.

**Pipeline:** `PDF → pdf2image → PaddleOCR → raw text → LLM → structured entities`

**Extracted entities:**
- Medications with dosage
- Lab values (glucose, hemoglobin, CRP, etc.)
- Diagnoses and clinical notes
- Document dates

---

### Module 4 — Sensor Scoring (Rule-based)

Evaluates physiological measurements from wearable devices against clinical thresholds.

| Metric | Normal range | Risk contribution |
|---|---|---|
| SpO₂ | ≥ 97% | `< 94%` → +0.40 · `94–96%` → +0.20 |
| Temperature | 36.1–37.2°C | `> 39.0°C` → +0.40 · `38.0–39.0°C` → +0.20 |
| Heart rate | 60–100 bpm | `< 50 or > 120` → +0.35 |
| Sleep | ≥ 7h | `< 4h` → +0.10 |

Final sensor score is capped at `1.0`.

---

### Module 5 — Multimodal Fusion

Combines all modality scores using a configurable weighted average. Missing modalities are excluded and their weights redistributed proportionally.

```python
def compute_global_score(modality_scores: dict[str, float], weights: dict[str, float]) -> float:
    active = {k: v for k, v in weights.items() if k in modality_scores}
    total_weight = sum(active.values())
    return sum(modality_scores[k] * w for k, w in active.items()) / total_weight
```

---

### Module 6 — Chat Assistant (RAG)

An LLM assistant grounded in the user's report via Retrieval-Augmented Generation.

**Pipeline:**
1. At report creation: embed report text with `all-MiniLM-L6-v2` → store chunks in Qdrant
2. At each user message: retrieve top-3 relevant chunks from Qdrant
3. Build contextual prompt: system + report context + chat history + user question
4. Stream response token by token via Server-Sent Events

**System prompt (enforced):**
```
You are an informative medical assistant. Answer questions based
solely on the provided report context. Always remind the user that
your responses do not replace professional medical advice.
```

---

## 📡 API Reference

All endpoints are prefixed with `/api/v1`.

### Submit an analysis

```http
POST /api/v1/analysis
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|---|---|---|---|
| `image` | File | No | JPEG or PNG photo |
| `pdf` | File | No | Medical PDF document |
| `symptom_text` | string | No | Free-text symptom description |
| `sensor_data` | JSON string | No | `{"spo2": 97, "temp": 38.1, "bpm": 72, "sleep_hours": 6.2}` |

At least one field is required.

**Response:**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

---

### Poll analysis status

```http
GET /api/v1/analysis/{analysis_id}/status
```

**Response:**
```json
{
  "status": "processing",
  "progress": 60,
  "stages": [
    { "name": "image",  "status": "done",       "summary": "Lesion detected (78%)" },
    { "name": "text",   "status": "done",       "summary": "3 symptoms extracted" },
    { "name": "sensor", "status": "processing", "summary": null },
    { "name": "fusion", "status": "pending",    "summary": null }
  ]
}
```

`status` values: `pending` · `processing` · `done` · `failed`

---

### Retrieve report

```http
GET /api/v1/report/{analysis_id}
```

**Response:**
```json
{
  "id": "uuid",
  "analysis_id": "uuid",
  "risk_level": "surveiller",
  "global_score": 0.54,
  "created_at": "2026-06-12T10:30:00Z",
  "recommendations": [
    "Consult a healthcare professional within 48 hours.",
    "Monitor temperature every 6 hours."
  ],
  "modality_results": [
    {
      "modality": "image",
      "risk_score": 0.78,
      "confidence": 0.78,
      "summary": "Skin lesion detected on left arm.",
      "raw_output": { ... }
    }
  ]
}
```

---

### Chat with the assistant

```http
POST /api/v1/chat
Content-Type: application/json
Accept: text/event-stream
```

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "What does the image show exactly?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

Returns an SSE stream of `text/event-stream` tokens.

---

### Export PDF report

```http
GET /api/v1/report/{analysis_id}/pdf
```

Returns a `application/pdf` binary download.

---

## 🖥 Frontend Screens

| Screen | Route | Description |
|---|---|---|
| **Input** | `/` | Upload image, PDF, enter symptoms, connect sensor data |
| **Analysis** | `/analysis/:id` | Real-time animated progress for each AI module |
| **Report** | `/report/:id` | Risk gauge, per-modality cards, recommendations, export |
| **Chat** | `/report/:id/chat` | RAG-powered assistant, quick-question chips, SSE streaming |

---

## 🗄 Database Schema

```sql
-- Core analysis record
CREATE TABLE analyses (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status      TEXT NOT NULL CHECK (status IN ('pending','processing','done','failed')),
    image_path  TEXT,
    pdf_path    TEXT,
    symptom_text TEXT,
    sensor_data JSONB
);

-- Per-modality AI results
CREATE TABLE modality_results (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    modality    TEXT NOT NULL CHECK (modality IN ('image','text','pdf','sensor','fusion')),
    raw_output  JSONB NOT NULL,
    risk_score  FLOAT NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
    confidence  FLOAT,
    summary     TEXT
);

-- Final generated report
CREATE TABLE reports (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id      UUID NOT NULL UNIQUE REFERENCES analyses(id) ON DELETE CASCADE,
    risk_level       TEXT NOT NULL CHECK (risk_level IN ('normal','surveiller','urgent')),
    global_score     FLOAT NOT NULL,
    recommendations  JSONB NOT NULL DEFAULT '[]',
    full_text        TEXT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chat history (linked to analysis context)
CREATE TABLE chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## ⚡ Async Pipeline

```
POST /api/v1/analysis
         │
         ├─ Save files → MinIO
         ├─ Create Analysis record (status=pending)
         ├─ Enqueue Celery task: run_analysis(analysis_id)
         └─ Return 202 { analysis_id }

         [Celery Worker]
         │
         ├─ Set status=processing
         │
         ├─ asyncio.gather([               ← parallel execution
         │     yolo_service.run(image),
         │     llm_service.run(text),
         │     ocr_service.run(pdf),
         │     sensor_service.run(data)
         │   ])
         │
         ├─ Save each ModalityResult as it completes
         │
         ├─ fusion_service.fuse(all_results)
         │
         ├─ report_service.generate(fusion_result)
         │
         ├─ embed_and_store(report) → Qdrant
         │
         └─ Set status=done

[Frontend polls GET /analysis/{id}/status every 2s
 until status=done, then navigates to /report/{id}]
```

---

## 🧑‍💻 Development Guide

### Running services individually

```bash
# Backend only (hot reload)
docker compose up postgres redis minio qdrant -d
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend only (hot reload)
cd frontend && npm run dev

# Celery worker
cd backend && celery -A app.tasks.analysis_tasks worker --loglevel=info

# Ollama (local GPU)
ollama serve
ollama pull llama3.1:8b
```

### Running database migrations

```bash
# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "add_chat_messages"

# Apply all pending migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Code quality

```bash
# Python — format + lint
cd backend
ruff format .
ruff check .
mypy app/

# TypeScript — lint + type check
cd frontend
npm run lint
npm run type-check
```

---

## 🧪 Testing

### Backend

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run a specific module
pytest tests/test_fusion.py -v
```

### Frontend

```bash
cd frontend

# Unit and component tests
npm run test

# End-to-end tests (Playwright)
npm run test:e2e
```

### Integration test with sample data

A sample test dataset is provided in `tests/fixtures/`:

```
tests/fixtures/
├── sample_lesion.jpg        # Test image with visible lesion
├── sample_report.pdf        # Simulated medical PDF
└── sample_sensor.json       # Wearable sensor readings
```

Run the full end-to-end flow:

```bash
python tests/integration/test_full_pipeline.py
```

---

## 🗺 Roadmap

- [x] Project architecture and design system
- [x] Docker Compose environment
- [ ] YOLOv11 fine-tuning on ISIC dataset
- [ ] FastAPI backend skeleton
- [ ] Celery async task pipeline
- [ ] React frontend — all 4 screens
- [ ] RAG chat assistant with Qdrant
- [ ] PDF report export
- [ ] Unit tests for all AI services
- [ ] End-to-end integration tests
- [ ] User authentication (optional)
- [ ] Multi-language support (FR / EN / AR)
- [ ] Mobile-responsive layout
- [ ] Demo deployment on Render / Railway

---

## 🤝 Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add sensor anomaly detection"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request against `main`

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages and ensure all tests pass before submitting.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## ⚠️ Medical Disclaimer

> **MultiMedAI is not a medical device and does not provide medical diagnoses.**
>
> This platform is an informational tool designed to help users organize and present health-related information. The risk assessments and recommendations generated by this system are **preliminary, non-clinical, and should never replace the advice, diagnosis, or treatment provided by a qualified healthcare professional.**
>
> If you are experiencing a medical emergency, call your local emergency services immediately.
>
> By using MultiMedAI, you acknowledge that the developers and contributors accept no liability for any health decisions made based on the platform's output.

---

<div align="center">

Built with care as a Final Year Project (PFE) · 2025–2026

</div>
