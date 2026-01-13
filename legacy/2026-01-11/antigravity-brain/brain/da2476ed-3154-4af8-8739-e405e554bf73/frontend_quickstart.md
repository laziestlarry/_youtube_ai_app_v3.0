# AutonomaX Frontend v3 - Quick Start Guide

## 🚀 Running the Application

### Frontend (Next.js 14)

```bash
cd frontend_v3
npm run dev -- -p 3001
```

Access at: `http://localhost:3001`

### Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Access at: `http://localhost:8000`

## ✨ New Features

### 1. **Opportunity Navigator**

- AI-powered business opportunity discovery
- Strategic blueprint generation
- Financial projections and market analysis
- Located at: `/` (homepage)

### 2. **AI Empire Genesis**

- Interactive build simulation
- Departmental task execution
- Located at: `/build`

### 3. **Shopify Integration**

- Autonomous SKU generation endpoint: `/api/agency/orchestrate/skigen`
- Admin API for product creation
- Storefront API for data retrieval

## 🔧 Configuration

### Environment Variables

Make sure these are set in `frontend_v3/.env.local`:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Genkit AI Flows

All AI flows now use: `googleai/gemini-1.5-flash-latest`

## 📝 Key Files

- **Frontend Entry**: `frontend_v3/src/app/page.tsx`
- **AI Flows**: `frontend_v3/src/ai/flows/`
- **Genkit Config**: `frontend_v3/src/ai/genkit.ts`
- **Shopify Service**: `backend/services/shopify_service.py`
- **Direction Board**: `modules/ai_agency/direction_board.py`

## 🎯 Next Steps

1. Test the Opportunity Navigator at `localhost:3001`
2. Try the AI business analysis flow
3. Configure Shopify credentials for SKU generation
4. Deploy frontend to production when ready

## 🐛 Troubleshooting

**Issue**: "Model not found" error
**Fix**: All AI flows have been updated to use `googleai/gemini-1.5-flash-latest`

**Issue**: Build errors
**Fix**: Run `npm install` in `frontend_v3` directory

**Issue**: API not responding
**Fix**: Ensure backend is running on port 8000
