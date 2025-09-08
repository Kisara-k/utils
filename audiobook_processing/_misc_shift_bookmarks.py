import sys
import fitz  # PyMuPDF
import os

def shift_toc(toc, shift=1):
    """
    Recursively shift TOC page numbers by 'shift'.
    PyMuPDF TOC: list of [level, title, page number]
    """
    return [[level, title, page + shift] for level, title, page in toc]

def fix_pdf(file_path):
    doc = fitz.open(file_path)
    
    # Get existing TOC
    toc = doc.get_toc()
    if not toc:
        print(f"No bookmarks found for: {file_path}")
    else:
        # Shift all TOC entries by 1 page
        new_toc = shift_toc(toc, shift=1)
        doc.set_toc(new_toc)
        print(f"Bookmarks shifted by 1 page for: {file_path}")

    # Save fixed PDF
    base, ext = os.path.splitext(file_path)
    output_path = f"{base}_fixed{ext}"
    doc.save(output_path)
    doc.close()
    print(f"Fixed PDF saved as: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Drag and drop a PDF onto this script to fix bookmarks.")
    else:
        for pdf_file in sys.argv[1:]:
            if os.path.isfile(pdf_file) and pdf_file.lower().endswith(".pdf"):
                fix_pdf(pdf_file)
            else:
                print(f"Not a valid PDF file: {pdf_file}")
