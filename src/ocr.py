from pdf2image import convert_from_path
import easyocr
import numpy as np

# =====================================================
# CONFIG
# =====================================================

MIN_CONFIDENCE = 0.50
MIN_MEANINGFUL_WORDS = 10

reader = easyocr.Reader(
    ["en"],
    gpu=False
)


# =====================================================
# QUALITY CHECK
# =====================================================

def count_meaningful_words(text):

    words = text.split()

    meaningful_words = [

        word

        for word in words

        if len(word) >= 4
        and any(
            ch.isalpha()
            for ch in word
        )

    ]

    return len(
        meaningful_words
    )


# =====================================================
# OCR PAGE
# =====================================================

def ocr_image(image):

    results = reader.readtext(
        image
    )

    extracted_lines = []

    confidences = []

    ocr_words = []

    word_index = 0

    for bbox, text, confidence in results:

        if confidence < MIN_CONFIDENCE:
            continue

        x_values = [
            p[0]
            for p in bbox
        ]

        y_values = [
            p[1]
            for p in bbox
        ]

        # ----------------------------------
        # Build PyMuPDF-compatible tuple
        # ----------------------------------

        ocr_words.append(

            (

                min(x_values),      # x0
                min(y_values),      # y0

                max(x_values),      # x1
                max(y_values),      # y1

                text,               # word text

                0,                  # block_no
                0,                  # line_no

                word_index          # word_no

            )

        )

        word_index += 1

        extracted_lines.append(
            text
        )

        confidences.append(
            confidence
        )

    extracted_text = "\n".join(
        extracted_lines
    )

    avg_confidence = (

        sum(confidences)
        /
        len(confidences)

        if confidences

        else 0

    )

    meaningful_words = (
        count_meaningful_words(
            extracted_text
        )
    )

    return {

        "text":
            extracted_text,

        "words":
            ocr_words,

        "avg_confidence":
            avg_confidence,

        "meaningful_words":
            meaningful_words

    }


# =====================================================
# SCANNED PAGE PROCESSOR
# =====================================================

def process_scanned_page(page):

    image = np.array(
        page.convert("RGB")
    )

    result = ocr_image(
        image
    )

    # ----------------------------------
    # Poor OCR
    # ----------------------------------

    if (
        result[
            "meaningful_words"
        ]
        <
        MIN_MEANINGFUL_WORDS
    ):

        return {

            "manual_review":
                True,

            "reason":
                "poor_ocr_quality",

            "words":
                [],

            "text":
                result["text"],

            "avg_confidence":
                result[
                    "avg_confidence"
                ]

        }

    # ----------------------------------
    # Good OCR
    # ----------------------------------

    return {

        "manual_review":
            False,

        "reason":
            None,

        "words":
            result["words"],

        "text":
            result["text"],

        "avg_confidence":
            result[
                "avg_confidence"
            ]

    }


# =====================================================
# PDF PROCESSOR
# =====================================================

def process_scanned_pdf(
    pdf_path
):

    pages = convert_from_path(
        pdf_path
    )

    results = []

    for page_number, page in enumerate(
        pages,
        start=1
    ):

        page_result = (
            process_scanned_page(
                page
            )
        )

        page_result[
            "page_number"
        ] = page_number

        results.append(
            page_result
        )

    return results


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    pdf_path = (
        r"YOUR_PDF_PATH"
    )

    results = (
        process_scanned_pdf(
            pdf_path
        )
    )

    for page in results:

        print("\n")
        print("=" * 80)

        print(
            f"PAGE "
            f"{page['page_number']}"
        )

        print("=" * 80)

        print(
            "Manual Review:",
            page[
                "manual_review"
            ]
        )

        print(
            "Average Confidence:",
            round(
                page[
                    "avg_confidence"
                ],
                2
            )
        )

        print(
            "Detected Words:",
            len(
                page["words"]
            )
        )

        if page["manual_review"]:

            print(
                "Reason:",
                page["reason"]
            )

        else:

            print(
                "\nFirst 10 words:\n"
            )

            for word in page[
                "words"
            ][:10]:

                print(word)

