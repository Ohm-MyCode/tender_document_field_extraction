from pdf2image import convert_from_path
import easyocr
import os
import numpy as np


print(os.getcwd())
reader = easyocr.Reader(["en"], gpu=False)


def extract_text_from_scanned_pdf(pdf_path: str) -> str:

    pages = convert_from_path(pdf_path)

    extracted_text = []

    for page in pages:
        # Convert PIL Image to numpy array
        image = np.array(page.convert("RGB"))

        results = reader.readtext(image)

        page_text = "\n".join(
            result[1]
            for result in results
        )

        extracted_text.append(page_text)
        for box, text, confidence in results:
            print(confidence, text)

    return "\n\n".join(extracted_text)



text = extract_text_from_scanned_pdf(
    "src/test.pdf"
)

print(text[:2000])