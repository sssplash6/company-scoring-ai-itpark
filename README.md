# IT Park company scoring

## Origin
This tool came from a real gap I saw while interning in the IT Park regional project management department. We were deciding which international businesses to approach for outsourcing based on subjective browsing of LinkedIn, Apollo, and company websites. I built this app to replace that subjective process with a consistent, evidence-based scoring approach.

The tool is currently **actively used in the regional project management department** for vendor screening.

## What it is
A local desktop app that accepts a company name, collects **public web data**, and produces a **scorecard + PDF/CSV/Excel** using an LLM. The API key is **required** and **not** stored. Users can choose which criteria to include.

## What it does
- Collects public info (company website, public pages, review sites, job postings, news mentions).
- Scores companies using a structured AI rubric with coverage and confidence.
- Exports PDF/CSV/Excel reports.

## What it does not do
- It does **not** scrape sites that forbid automation (e.g., LinkedIn/Apollo). If you want that data, add manual inputs or approved APIs.
- It does **not** store API keys.

## Features
- Criteria selection by category.
- Float-based scores with coverage and confidence.
- Disqualifies companies with no public info or no English support.
- Local caching of public pages for auditability.

## Tech stack
- Python 3.10+
- PySide6 (desktop UI)
- Requests + BeautifulSoup + lxml (public data collection)
- OpenAI API (LLM scoring)
- SQLite (local cache)

## Quick start (dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e /Users/workingmyassof/itparl
python -m itpark_scoring.app
```

## Run on Windows
If you have the `.exe` (from Releases or your internal distribution), just run it:
1. Download `itpark-scoring.exe`
2. Double-click to launch

## Run on macOS
```bash
python -m itpark_scoring.app
```


## Configuration
- Enter your OpenAI API key in the UI. The key is required, held in memory only, and cleared when the app exits.

## Data and compliance
- The collector respects robots.txt where possible. If a site disallows crawling, it is skipped.
- Always review each target site's Terms of Service.

## Roadmap ideas
- Add approved data sources via APIs.
- Add regional weighting presets.
- Add side-by-side comparisons.

## License
Proprietary. All rights reserved.

## Disclaimer
This tool provides decision support based on public information. Always validate critical business decisions with human review.
