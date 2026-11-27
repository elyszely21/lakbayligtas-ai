# LakbayLigtas AI

A Streamlit preparation assistant for hiking, camping, trekking, and sightseeing in
Cebu and the Philippines. It offers general preparation guidance; it does not have
live weather or trail information.

## Feature status

| Original feature | Status | What is currently available |
| --- | --- | --- |
| Smart Adventure Planner | Partial | Generates an itinerary and a Before You Go section through the configured AI service. The checklist section in the planner is still a placeholder. |
| Gear and Packing Checklist | Working | Static activity-specific essentials and optional items, progress tracking, and Markdown export. |
| Adventure Readiness Assessment | Working | Deterministic self-check scoring with up to three improvement areas. It is not a guarantee of safety. |
| Outdoor Safety Guide | Working | Fixed scenario buttons and free-text questions use the shared safety pipeline. AI-generated advice is general; contact local authorities or emergency services for real emergencies. |
| Budget Estimator | Working | Calculates low/high PHP estimates locally from `data/cost_estimates.json`; the AI does not do the arithmetic. Values are estimates, not current local prices. |
| Responsible Travel Tips | Partial | Leave No Trace items are included in the checklist, and the assistant has responsible-travel guidance. There is no dedicated tips page yet. |
| Alternative Adventure Suggestions | Partial | The assistant can suggest alternatives in conversation; there is no dedicated alternatives page yet. |
| Chat Assistant | Working | Conversational outdoor-preparation help, using the configured Aiki Labs API and shared input/output defenses. |

“Working” AI features require an available Aiki Labs API key. AI requests go through
`core/pipeline.py` and `core/llm_client.py`; the app applies input filtering, token
wrapping, output checking, and a 15-request session cap. Tests mock the AI client and
do not make real API calls.

## Setup

Requires Python 3.12.

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Configure `LLM_API_KEY` through the local Streamlit configuration or deployment
environment. Never commit API keys, `.env` files, or Streamlit secrets.

## Tests

```powershell
python -m pytest -q
```

## Important limitations

- Budget ranges are general estimates. Verify costs, permits, and advisories with the
  local tourism office or site management, and check PAGASA for weather.
- The app has no live trail, closure, permit, or weather data. It does not guarantee
  that any destination or route is safe.
- Readiness results are a self-check only, not a medical assessment or safety
  certification.
- The planner's checklist result area is not yet connected to the interactive Gear
  Checklist page.
