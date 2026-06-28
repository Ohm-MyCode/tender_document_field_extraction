import re

# =====================================================
# PATTERNS FOR MATCHING 
# =====================================================

PO_PATTERN = r"GEMC-\d+"

BID_PATTERN = r"GEM/\d{4}/B/\d+"

DATE_PATTERN = (
    r"(?:"
    r"\d{2}[./-]\d{2}[./-]\d{4}"
    r"|"
    r"\d{2}-[A-Za-z]{3}-\d{4}"
    r")"
)

INVOICE_PATTERN = (
    r"(?:"
    r"GEM-\d+"
    r"|"
    r"[A-Z]{2,5}\d{4,}"
    r")"
)

PERCENT_PATTERN = r"\d+(?:\.\d+)?%"

# =====================================================
# ROW BUILDER
# =====================================================

def build_rows(words):

    rows = {}

    for w in words:

        row_key = round(w[1])

        rows.setdefault(row_key, []).append({

            "x0": w[0],
            "y0": w[1],
            "x1": w[2],
            "y1": w[3],
            "text": w[4]

        })

    for row in rows.values():

        row.sort(
            key=lambda x: x["x0"]
        )

    return rows


def row_text(row):

    return " ".join(
        word["text"]
        for word in row
    )


# =====================================================
# GENERIC HELPERS
# =====================================================

def regex_word_in_row(row, pattern):

    for word in row:

        if re.fullmatch(
            pattern,
            word["text"],
            re.IGNORECASE
        ):

            return word

    return None


def regex_words_in_row(row, pattern):

    matches = []

    for word in row:

        if re.fullmatch(
            pattern,
            word["text"],
            re.IGNORECASE
        ):

            matches.append(word)

    return matches


def extract_after_label(
    row,
    labels,
    validator
):

    words_lower = [

        w["text"].lower().replace(":", "")

        for w in row

    ]

    best_end_index = None

    for label in labels:

        label_parts = [

            x.replace(":", "")

            for x in label.lower().split()

        ]

        for i in range(len(words_lower)):

            if i + len(label_parts) > len(words_lower):
                continue

            candidate = words_lower[
                i:i + len(label_parts)
            ]

            if candidate == label_parts:

                best_end_index = (
                    i + len(label_parts)
                )

    if best_end_index is None:
        return None

    for i in range(
        best_end_index,
        len(row)
    ):

        text = row[i]["text"]

        if re.fullmatch(
            validator,
            text,
            re.IGNORECASE
        ):

            return row[i]

    return None


# =====================================================
# BID RECORDS
# =====================================================

def extract_bid_records(page):

    rows = build_rows(
        page["words"]
    )

    records = []

    for row in rows.values():

        text = row_text(row).lower()

        if (
            "bid" not in text
            and
            "bid/ra" not in text
        ):
            continue

        bid_word = regex_word_in_row(
            row,
            BID_PATTERN
        )

        if bid_word:

            records.append({

                "field": "bid_record",

                "bid_number":
                    bid_word["text"],

                "page":
                    page["page_number"]

            })

    return records


# =====================================================
# PO RECORDS
# =====================================================

def extract_po_records(page):

    rows = build_rows(
        page["words"]
    )

    po_number = None
    po_date = None

    for row in rows.values():

        text = row_text(
            row
        ).lower()

        # ------------------------
        # PO NUMBER
        # ------------------------

        if (
            "order number" in text
            or
            "order no" in text
            or
            "gem po" in text
        ):

            po = extract_after_label(

                row,

                [

                    "order number",

                    "order no",

                    "gem po no"

                ],

                PO_PATTERN

            )

            if po:

                po_number = po["text"]

        # ------------------------
        # PO DATE
        # ------------------------

        if (
            "order date" in text
            or
            "po date" in text
        ):

            date_word = extract_after_label(

                row,

                [

                    "order date",

                    "po date"

                ],

                DATE_PATTERN

            )

            if date_word:

                po_date = date_word["text"]

    if (
        po_number is None
        and
        po_date is None
    ):

        return []

    return [{

        "field":
            "po_record",

        "po_number":
            po_number,

        "po_date":
            po_date,

        "page":
            page["page_number"]

    }]


# =====================================================
# INVOICE RECORD
# =====================================================

def extract_invoice_record(page):

    rows = build_rows(
        page["words"]
    )

    record = {

        "invoice_number": None,

        "invoice_date": None,

        "po_number": None,

        "po_date": None
    }

    for row in rows.values():

        text = row_text(row).lower()

        # --------------------------------
        # INVOICE NUMBER
        # --------------------------------

        if "invoice" in text:

            invoice = extract_after_label(

                row,

                [

                    "gem invoice no",

                    "invoice no",

                    "invoice number",

                    "tax invoice no",

                    "tax inv no"

                ],

                INVOICE_PATTERN

            )

            if invoice:

                record["invoice_number"] = {

                    "value":
                        invoice["text"],

                    "bbox":
                        invoice
                }

        # --------------------------------
        # INVOICE DATE
        # --------------------------------

        if "invoice" in text and "date" in text:

            invoice_date = extract_after_label(

                row,

                [

                    "gem invoice date",

                    "invoice date",

                    "tax invoice date"

                ],

                DATE_PATTERN

            )

            if invoice_date:

                record["invoice_date"] = {

                    "value":
                        invoice_date["text"],

                    "bbox":
                        invoice_date
                }

        # --------------------------------
        # PO NUMBER
        # --------------------------------

        if (
            "order number" in text
            or
            "order no" in text
        ):

            po = extract_after_label(

                row,

                [

                    "order number",

                    "order no",

                    "gem po no"

                ],

                PO_PATTERN

            )

            if po:

                record["po_number"] = {

                    "value":
                        po["text"],

                    "bbox":
                        po
                }

        # --------------------------------
        # PO DATE
        # --------------------------------

        if "order date" in text:

            po_date = extract_after_label(

                row,

                [

                    "order date",

                    "po date"

                ],

                DATE_PATTERN

            )

            if po_date:

                record["po_date"] = {

                    "value":
                        po_date["text"],

                    "bbox":
                        po_date
                }

    return record


# =====================================================
# PURCHASER
# =====================================================

def extract_purchaser(page):

    rows = build_rows(
        page["words"]
    )

    purchaser_labels = [

        "organisation name",

        "buyer name",

        "billed to",

        "bill to",

        "shipping to"

    ]

    for row in rows.values():

        text = row_text(row).lower()

        for label in purchaser_labels:

            if label in text:

                return {

                    "field": "purchaser",

                    "value":
                        row_text(row),

                    "page":
                        page["page_number"]

                }

    return None


# =====================================================
# LOCAL CONTENT
# =====================================================

def extract_local_content(page):

    rows = build_rows(
        page["words"]
    )

    LOCAL_CONTENT_KEYWORDS = [

        "local content",

        "% of local content",

        "percentage of local content",

        "percent of local content"
    ]

    records = []

    for row in rows.values():

        text = row_text(
            row
        ).lower()

        if not any(
            keyword in text
            for keyword in LOCAL_CONTENT_KEYWORDS
        ):
            continue

        percentages = regex_words_in_row(
            row,
            PERCENT_PATTERN
        )

        for pct in percentages:

            records.append({

                "field":
                    "local_content",

                "value":
                    pct["text"],

                "page":
                    page["page_number"]

            })

    return records


# =====================================================
# CERTIFICATES
# =====================================================

CERTIFICATE_KEYWORDS = [

    "completion certificate",

    "certificate of completion",

    "work completion certificate",

    "execution certificate",

    "certificate of execution",

    "performance certificate",

    "satisfactory performance"

]


def detect_certificates(page):

    text = page["text"].lower()

    results = []

    for keyword in CERTIFICATE_KEYWORDS:

        if keyword in text:

            results.append({

                "field":
                    "certificate",

                "value":
                    keyword,

                "page":
                    page["page_number"]

            })

    return results


# =====================================================
# TEST
# Testing would require "import fitz" and load_pdf from main.py
# =====================================================

"""if __name__ == "__main__":

    pdf_path = r"PATH_TO_YOUR_PDF"

    pages = load_pdf(pdf_path)

    for page in pages:

        po_records = extract_po_records(page)

        bid_records = extract_bid_records(page)

        invoice_record = extract_invoice_record(page)

        purchaser = extract_purchaser(page)

        local_content = extract_local_content(page)

        certificates = detect_certificates(page)

        if any([

            po_records,

            bid_records,

            invoice_record["invoice_number"],

            invoice_record["invoice_date"],

            invoice_record["po_number"],

            invoice_record["po_date"],

            purchaser,

            local_content,

            certificates

        ]):

            print("\n")
            print("=" * 100)
            print(f"PAGE {page['page_number']}")
            print("=" * 100)

            print("PO RECORDS:")
            print(po_records)

            print("\nBID RECORDS:")
            print(bid_records)

            print("\nINVOICE RECORD:")
            print(invoice_record)

            print("\nPURCHASER:")
            print(purchaser)

            print("\nLOCAL CONTENT:")
            print(local_content)

            print("\nCERTIFICATES:")
            print(certificates)"""