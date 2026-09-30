import json
import os
from pathlib import Path

from dotenv import load_dotenv
from ollama import Client
from pydantic import BaseModel


# Load environment variables
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

client = Client(host=OLLAMA_URL)


class ContactDetails(BaseModel):
    address_1: str = "Not available"
    address_2: str = "Not available"
    phone: str = "Not available"
    email: str = "Not available"
    contact_person: str = "Not available"


class SupplierSummary(BaseModel):
    supplier_name: str
    products_services: list[str]
    contact_details: ContactDetails
    warranty: str
    delivery_terms: str
    sources: list[str]

# Read supplier pages
DATA_DIR = Path("data/supplier1")


def read_pages():
    pages = {}

    for file_name in ["home.txt", "about.txt", "contact.txt"]:
        file_path = DATA_DIR / file_name

        text = file_path.read_text(encoding="utf-8").strip()

        pages[file_name] = text

    return pages


def build_prompt(pages):
    return f"""
Extract supplier information from the following pages.

Rules:
1. Use ONLY the provided text.
2. Do NOT guess or invent information.
3. If information is missing, return "Not available".
4. products_services MUST be a JSON list.
5. contact_details MUST be a JSON object.
6. Return ONLY valid JSON.

Required fields:

supplier_name: string

products_services: list of strings

contact_details:
- address_1
- address_2
- phone
- email
- contact_person

warranty: string

delivery_terms: string

sources: list of page names and URLs

SOURCE PAGE: home.txt
{pages["home.txt"]}

SOURCE PAGE: about.txt
{pages["about.txt"]}

SOURCE PAGE: contact.txt
{pages["contact.txt"]}
"""


# Call Gemma
def generate_summary(prompt):
    response = client.chat(
    model=OLLAMA_MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    format=SupplierSummary.model_json_schema(),
)

    return response.message.content


# Main program
def main():
    print("Reading supplier pages...")

    pages = read_pages()

    prompt = build_prompt(pages)

    print("Sending information to Gemma 4...")

    result = generate_summary(prompt)

    # Convert Gemma JSON string into Python dictionary
    data = json.loads(result)

    # Validate using Pydantic
    summary = SupplierSummary.model_validate(data)

    # Save output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "supplier_summary.json"

    output_file.write_text(
        summary.model_dump_json(indent=2),
        encoding="utf-8",
    )

    # Display readable summary
    print("\n========== SUPPLIER SUMMARY ==========")

    print(f"\nSupplier: {summary.supplier_name}")

    print("\nProducts / Services:")
    for product in summary.products_services:
        print(f"- {product}")

    print(f"\nContact: {summary.contact_details}")
    print(f"Warranty: {summary.warranty}")
    print(f"Delivery: {summary.delivery_terms}")

    print("\nSources:")
    for source in summary.sources:
        print(f"- {source}")

    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()