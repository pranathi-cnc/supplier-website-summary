 Supplier Website Summary

A simple Python application that extracts supplier information from saved
website pages and generates a short factual summary using a local Gemma 4
model through Ollama.

## Tech Stack

- Python
- Ollama
- Gemma 4
- BeautifulSoup
- Pydantic

## Project Structure

```text
supplier-website-summary/
├── data/
│   └── supplier1/
│       ├── home.html
│       ├── about.html
│       └── contact.html
├── output/
│   └── supplier_summary.json
├── src/
│   └── supplier_summary.py
├── .env
├── requirements.txt
└── README.md



Setup

Create and activate the virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create .env:

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:latest

Make sure Ollama is running and the model is available:

ollama list
ollama run gemma4:latest
Run
python src\supplier_summary.py

The application:

Reads the three HTML pages.
Cleans the HTML using BeautifulSoup.
Sends the cleaned content to Gemma 4.
Extracts supplier information.
Validates the response using Pydantic.
Generates a short supplier summary.
Saves the structured result to output/supplier_summary.json.
Sample Input

Supplier:

Bharat Industrial Supplier

Input pages:

data/supplier1/home.html
data/supplier1/about.html
data/supplier1/contact.html
Sample Output
========== SUPPLIER SUMMARY ==========

Supplier: Bharat Industrial Supplier

Summary:
Bharat Industrial Supplier, established in 1976, is an ISO 9001:2015
supplier, manufacturer, exporter, trader and wholesaler of fasteners
and industrial products.

Saved to: output\supplier_summary.json
Gemma Model

Exact local model:

gemma4:latest

The prompt instructs Gemma to:

Use only the supplied website content.
Extract factual supplier information.
Not guess or invent information.
Return Not available when information is missing.
Generate a short 2–3 sentence summary mainly from the About page.
Mistake and Improvement

Mistake: Gemma initially treated enquiry/quotation messages as warranty
and delivery information and sometimes returned generic product information.

Check: The generated output was compared with the actual text extracted
from the HTML pages.

Change: Improved HTML cleaning and added stricter prompt instructions
to ignore enquiry messages and never infer missing warranty or delivery
information.