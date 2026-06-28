import fitz
import io
import os
import sys
import pandas as pd

from PIL import Image

from src import extractor
from src import ocr
from src import aggregator

# =====================================================
# PAGE CLASSIFIER
# =====================================================

def is_scanned_page(page):

    text = page.get_text("text").strip()

    return len(text) < 50


# =====================================================
# EXTRACTION WRAPPER
# =====================================================

def run_extraction(page_data):

    return {

        "page":
            page_data["page_number"],

        "manual_review":
            False,

        "po_records":
            extractor.extract_po_records(
                page_data
            ),

        "bid_records":
            extractor.extract_bid_records(
                page_data
            ),

        "invoice_record":
            extractor.extract_invoice_record(
                page_data
            ),

        "purchaser":
            extractor.extract_purchaser(
                page_data
            ),

        "local_content":
            extractor.extract_local_content(
                page_data
            ),

        "certificates":
            extractor.detect_certificates(
                page_data
            )
    }


# =====================================================
# DIGITAL PAGE
# =====================================================

def process_digital_page(page, page_number):

    page_data = {

        "page_number":
            page_number,

        "text":
            page.get_text("text"),

        "words":
            page.get_text("words")
    }

    return run_extraction(page_data)


# =====================================================
# SCANNED PAGE
# =====================================================

def process_scanned_page(page, page_number):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2)
    )

    image = Image.open(
        io.BytesIO(
            pix.tobytes("png")
        )
    )

    ocr_result = ocr.process_scanned_page(
        image
    )

    if ocr_result["manual_review"]:

        return {

            "page":
                page_number,

            "manual_review":
                True,

            "reason":
                ocr_result["reason"]
        }

    page_data = {

        "page_number":
            page_number,

        "text":
            ocr_result["text"],

        "words":
            ocr_result["words"]
    }

    return run_extraction(page_data)


# =====================================================
# PDF PROCESSOR
# =====================================================

def process_pdf(pdf_path):

    results = []

    doc = fitz.open(pdf_path)

    for page_number, page in enumerate(
        doc,
        start=1
    ):

        print(
            f"\nProcessing Page "
            f"{page_number}"
        )

        if is_scanned_page(page):

            print(
                "SCANNED PAGE"
            )

            result = process_scanned_page(
                page,
                page_number
            )

        else:

            print(
                "DIGITAL PAGE"
            )

            result = process_digital_page(
                page,
                page_number
            )

        results.append(
            result
        )

    doc.close()

    return results


# =====================================================
# FOLDER PROCESSOR
# =====================================================

def process_folder(folder_path):

    all_results = []

    for root, dirs, files in os.walk(
        folder_path
    ):

        for file in files:

            if not file.lower().endswith(
                ".pdf"
            ):
                continue

            pdf_path = os.path.join(
                root,
                file
            )

            print(
                f"\nProcessing PDF:"
                f" {pdf_path}"
            )

            pdf_results = process_pdf(
                pdf_path
            )

            bidder_name = (
                os.path.basename(root)
            )

            for record in pdf_results:

                record["pdf_name"] = file

                record["bidder"] = bidder_name

                all_results.append(
                    record
                )

    return all_results


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python main.py "
            "<folder_path>"
        )

        sys.exit(1)

    folder_path = sys.argv[1]

    results = process_folder(
        folder_path
    )
    summary_rows = (
        aggregator.build_summary_rows(
            results
        )
    )
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(summary_rows)

    df.to_csv(
        os.path.join("output", "summary_output.csv"),
        index=False,encoding="utf-8-sig"
    )

    print("Summary saved to summary_output.csv")

    """print(
        f"\nTotal Pages Processed: "
        f"{len(results)}"
    )"""
    print(
    f"\nTotal Pages Processed: "
    f"{len(results)}"
)

for result in results:

    print("\n" + "=" * 80)

    print(
        f"PDF: {result['pdf_name']}"
    )

    print(
        f"Bidder: {result['bidder']}"
    )

    print(
        f"Page: {result['page']}"
    )

    print(
        f"Manual Review: "
        f"{result['manual_review']}"
    )
    if result["manual_review"]:

         print(
            f"Reason: "
            f"{result['reason']}"
    )

         continue

    print(
        f"PO Records: "
        f"{result['po_records']}"
    )
    print(
        f"Invoice Records: "
        f"{result['invoice_record']}"
    )

    print(
        f"Bid Records: "
        f"{result['bid_records']}"
    )
    print(
        f"local: "
        f"{result['local_content']}"
    )