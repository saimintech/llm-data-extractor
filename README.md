# llm-data-extractor

A small Flask API that loads a web page in headless Chrome, converts it to Markdown, and asks an LLM to return the fields you name as structured JSON (also saved as JSON and Excel files).

## How it works

```
POST /process {url, fields, type}
    |
    v
Selenium + headless Chrome   (random User-Agent, scrolls to the bottom)
    |
    v
BeautifulSoup (drop <header>/<footer>) -> html2text (Markdown)
    |                                         '--> output/rawData_<ts>.md
    v
Pydantic model built from `fields`
    |
    v
LLM (OpenAI / Gemini / Groq / local LM Studio)
    |
    v
{"listings": [ {field: value, ...}, ... ]}
    '--> output/sorted_data_<ts>.json and .xlsx
```

- `app.py`: Flask app with one endpoint, `POST /process`, listening on `0.0.0.0:5000`.
- `extractor.py`: Selenium setup, HTML cleanup and Markdown conversion, dynamic Pydantic models, per-provider LLM calls, file output and a token cost estimate printed to the console.
- `assets.py`: User-Agent list, Chrome options, model names, price table and prompts.

Every requested field is extracted as a string. OpenAI and Gemini get the Pydantic schema as a structured output format; the Groq and LM Studio paths put the schema in the system prompt and parse the reply with `json.loads`.

## API

```bash
curl -X POST http://localhost:5000/process \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com/listings", "fields": "title,price,location", "type": "gpt-4o-mini"}'
```

| Field | Description |
|-------|-------------|
| `url` | Page to load |
| `fields` | Comma separated field names to extract |
| `type` | Model to use (see below). Send it explicitly; there is no working default when it is omitted. |

Supported `type` values (as hardcoded in `extractor.py`):

| `type` | Provider |
|--------|----------|
| `gpt-4o-mini`, `gpt-4o-2024-08-06` | OpenAI |
| `gemini-1.5-flash` | Google Gemini |
| `Groq Llama3.1 70b` | Groq |
| `Llama3.1 8B` | Local LM Studio server at `http://localhost:1234/v1` |
| `selenium` | No LLM; returns the raw page HTML |

The response is `{"result": ...}`. On failure the error message is returned in `result`. Provider model IDs are hardcoded in `extractor.py` and `assets.py`; some may since have been retired by the providers, so check them before use.

## Stack

Python 3, Flask, Selenium with webdriver-manager and Google Chrome, BeautifulSoup, html2text, Pydantic, tiktoken, pandas/openpyxl, and the OpenAI, Groq and Google Generative AI SDKs.

## Setup

`setup.sh` targets Debian/Ubuntu. It installs Python and Google Chrome from Google's apt repository, creates a virtualenv at `<dir>/venv`, and installs `requirements.txt`. Run it from the repo root:

```bash
bash setup.sh .
cp .env.example .env      # then fill in the keys you need
./venv/bin/python app.py
```

To keep it running under PM2:

```bash
pm2 start venv/bin/python --name llm-data-extractor -- app.py
```

## Configuration

Read from `.env` via python-dotenv. Only the key for the provider you use is required.

| Variable | Used for |
|----------|----------|
| `OPENAI_API_KEY` | `gpt-4o-mini`, `gpt-4o-2024-08-06` |
| `GOOGLE_API_KEY` | `gemini-1.5-flash` |
| `GROQ_API_KEY` | `Groq Llama3.1 70b` |

## Security note

The API has no authentication and will load any URL it is given in a real browser. Run it on a private network or behind an authenticating proxy.

## Author

Built by Saim Safdar - https://saim.me
