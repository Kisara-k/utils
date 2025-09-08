import fitz  # PyMuPDF
import sys
import os

# Define phrases to redact
PHRASES_TO_REDACT = [
    "OceanofPDF.com",
    "https://oceanofpdf.com/"
]

# Get the list of files dragged onto the script
pdf_files = sys.argv[1:]  # Skip the script name

if not pdf_files:
    print("No files were dragged onto the script. Exiting.")
    input("Press Enter to exit...")
    sys.exit()

for filepath in pdf_files:
    if not filepath.lower().endswith(".pdf"):
        print(f"Skipped (not a PDF): {filepath}")
        continue

    filename = os.path.basename(filepath)
    print(f"Processing: {filename}")

    doc = fitz.open(filepath)

    for page in doc:
        for phrase in PHRASES_TO_REDACT:
            for inst in page.search_for(phrase):
                page.add_redact_annot(inst, fill=(1, 1, 1))
        page.apply_redactions()

    output_path = os.path.join(os.path.dirname(filepath), f"redacted_{filename}")
    doc.save(output_path)
    doc.close()
    print(f"Saved redacted PDF to: {output_path}")

print("All files have been redacted and saved.")
input("Press Enter to exit...")
