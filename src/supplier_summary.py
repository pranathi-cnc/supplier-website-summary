import json
import os
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ollama import Client
from pydantic import BaseModel


load_dotenv()

client = Client(host=os.getenv("OLLAMA_URL"))
MODEL = os.getenv("OLLAMA_MODEL")

DATA_DIR = Path("data/supplier1")


class ContactDetails(BaseModel):
    address_1: str = "Not available"
    address_2: str = "Not available"
    phone: str = "Not available"
    email: str = "Not available"
    contact_person: str = "Not available"


class SupplierSummary(BaseModel):
    supplier_name: str
    summary: str
    products_services: list[str]
    contact_details: ContactDetails
    warranty: str
    delivery_terms: str
    sources: list[str]


def clean_html(file_path):
    soup = BeautifulSoup(
        file_path.read_text(encoding="utf-8"),
        "html.parser"
    )

    for tag in soup([
        "script", "style", "nav", "header", "footer",
        "form", "button", "iframe", "noscript"
    ]):
        tag.decompose()

    lines = []
    for line in soup.get_text("\n", strip=True).splitlines():
        line = " ".join(line.split())
        if line and line not in lines:
            lines.append(line)

    return "\n".join(lines)


def read_pages():
    pages = {}

    for name in ["home.html", "about.html", "contact.html"]:
        pages[name] = clean_html(DATA_DIR / name)

    return pages


def build_prompt(pages):
    return f"""
Extract supplier information ONLY from the website text below.

Rules:
- Use only the supplied text.
- Never guess or invent information.
- Missing information must be "Not available".
- Ignore menus, forms, buttons and website boilerplate.
- Return only valid JSON.

SUMMARY:
Generate a short factual 2-3 sentence paragraph about the supplier.
Include the supplier name, what the company does, main product/service
categories, and important facts such as establishment year or
certification when explicitly available.
Do not list every product.
Do not include contact, warranty or delivery information.

PRODUCTS:
Extract the actual products mentioned.

CONTACT:
Extract the actual address, phone, email and contact person.

WARRANTY:
Extract only an actual warranty statement.
Otherwise return "Not available".

DELIVERY:
Extract only actual delivery/shipping/dispatch information.
Otherwise return "Not available".

SOURCES:
Use only:
["home.html", "about.html", "contact.html"]

======== HOME.HTML ========
{pages["home.html"]}

======== ABOUT.HTML ========
{pages["about.html"]}

======== CONTACT.HTML ========
{pages["contact.html"]}

Return only the JSON object.
"""


def generate_summary(prompt):
    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict factual information extraction "
                    "system. Never invent or infer facts."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        format=SupplierSummary.model_json_schema(),
        options={"temperature": 0},
    )

    return response.message.content


def main():
    print("Reading supplier pages...")
    pages = read_pages()

    print("Sending information to Gemma 4...")
    result = generate_summary(build_prompt(pages))

    summary = SupplierSummary.model_validate(json.loads(result))

    output = Path("output")
    output.mkdir(exist_ok=True)

    output_file = output / "supplier_summary.json"
    output_file.write_text(
        summary.model_dump_json(indent=2),
        encoding="utf-8"
    )

    print("\n========== SUPPLIER SUMMARY ==========")
    print(f"\nSupplier: {summary.supplier_name}")
    print(f"\n{summary.summary}")
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()