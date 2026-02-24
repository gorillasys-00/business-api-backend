# AI Business Suite - Technical Documentation (Backend)

## 1. Overview
This backend provides high-performance, deterministic AI-driven business intelligence via the Google Gemini API.

## 2. Core Architecture
- **Framework**: FastAPI
- **AI Model**: Google Gemini 2.5 Flash
- **Data Safety**: Pydantic models for structured output enforcement.

## 3. Deterministic AI Strategy
To ensure enterprise-grade reliability, the following configurations are enforced:
- **Temperature**: `0.0` (Stochasticity removed)
- **Seed**: `42` (Fixed mathematical seed)
- **Structured Outputs**: Pydantic schemas used in `GenerateContentConfig` to prevent JSON parsing errors.

## 4. In-Memory Caching System
Implemented in `v1.1.8` to eliminate redundant API costs and provide instant responses.
- **Mechanism**: Global dictionary-based lookup at the router level.
- **Scope**: Applied to all AI endpoints (ESG, Web Extract, Niche Data, etc.).
- **TTL**: Current session persistence. (Note: Restarts on server reboot).

## 5. API Endpoints
- `/api/v1/esg-score`: ESG scoring by company name.
- `/api/v1/niche-data`: Trend analysis by keyword.
- `/api/v1/web-extract`: Context-aware web data extraction.
- `/api/v1/text-to-json`: Unstructured text restructuring.
- `/api/v1/ai-scrape`: Low-level markdown extraction.

## 6. Security
- **Auth**: X-RapidAPI-Key verification.
- **Environment**: Managed via `.env` file.
