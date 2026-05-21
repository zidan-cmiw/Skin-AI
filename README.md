# AI SkinCare — Local Flask demo

This project is a small demo that accepts a face photo upload and (optionally)
calls OpenAI's vision-capable Responses API to analyze skin type and recommend
skincare categories.

Setup

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate  # on Windows PowerShell
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key (optional — if not set, the app falls back to a simple simulated analysis):

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

Or create a `.env` file next to `app.py` with:

```
OPENAI_API_KEY=sk-...
```

Run

```bash
python app.py
```

Open http://127.0.0.1:5000/analyze to upload an image and try the analysis.

Notes

- The OpenAI Responses API usage in `app.py` is a best-effort integration and
  may require adapting the request payload or the parsing logic depending on
  the exact model and API contract available to your OpenAI account.
- If you prefer to use a GROQ endpoint instead of OpenAI, set `GROQ_API_KEY`
  and (optionally) `GROQ_API_URL` in `.env`. The app will use GROQ when
  `GROQ_API_KEY` is present and fall back to OpenAI if not.
- Do not commit your API key to source control.