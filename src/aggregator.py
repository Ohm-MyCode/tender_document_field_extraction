# src/aggregator.py

def build_summary_rows(all_results):

    bidders = {}

    for record in all_results:

        bidder = record["bidder"]

        if bidder not in bidders:

            bidders[bidder] = {

                "bidder_name": bidder,

                "purchaser_name": None,

                "po_records": set(),

                "invoice_records": set(),

                "bid_numbers": set(),

                "local_content": set(),

                "completion_certificate": False,

                "manual_review": False,

                "pdf_number": None,

                "page_number": None
            }

        summary = bidders[bidder]

        # =====================================
        # PURCHASER
        # =====================================

        if (
            summary["purchaser_name"] is None
            and record.get("purchaser")
        ):

            summary["purchaser_name"] = (
                record["purchaser"]["value"]
            )
        # =====================================
        # BID RECORDS
        # =====================================

        for bid in record.get("bid_records", []):

            summary["bid_numbers"].add(
                bid["bid_number"]
            )

        # =====================================
        # PO RECORDS
        # =====================================

        for po in record.get(
            "po_records",
            []
        ):

            summary[
                "po_records"
            ].add(

                (
                    po.get(
                        "po_number"
                    ),

                    po.get(
                        "po_date"
                    )
                )
            )

        # =====================================
        # INVOICE RECORDS
        # =====================================

        invoice = record.get(
            "invoice_record",
            {}
        )

        if invoice:

            invoice_number = None
            invoice_date = None

            if (
                invoice.get(
                    "invoice_number"
                )
                and invoice[
                    "invoice_number"
                ]
            ):

                invoice_number = (
                    invoice[
                        "invoice_number"
                    ]["value"]
                )

            if (
                invoice.get(
                    "invoice_date"
                )
                and invoice[
                    "invoice_date"
                ]
            ):

                invoice_date = (
                    invoice[
                        "invoice_date"
                    ]["value"]
                )

            if invoice_number:

                summary[
                    "invoice_records"
                ].add(

                    (
                        invoice_number,
                        invoice_date
                    )
                )

        # =====================================
        # LOCAL CONTENT
        # =====================================

        for item in record.get(
            "local_content",
            []
        ):

            summary[
                "local_content"
            ].add(
                item["value"]
            )

        # =====================================
        # CERTIFICATES
        # =====================================

        if record.get(
            "certificates"
        ):

            summary[
                "completion_certificate"
            ] = True

        # =====================================
        # MANUAL REVIEW
        # =====================================

        if record.get(
            "manual_review"
        ):

            summary[
                "manual_review"
            ] = True

            if (
                summary["pdf_number"]
                is None
            ):

                summary[
                    "pdf_number"
                ] = record[
                    "pdf_name"
                ]

                summary[
                    "page_number"
                ] = record[
                    "page"
                ]

    # =====================================
    # BUILD FINAL ROWS
    # =====================================

    rows = []

    serial_no = 1

    for bidder, summary in bidders.items():

        po_lines = []

        for po_number, po_date in sorted(
            summary["po_records"]
        ):

            if not po_number:
                continue

            if po_date:

                po_lines.append(
                    f"{po_number} ({po_date})"
                )

            else:

                po_lines.append(
                    f"{po_number}"
                )

        invoice_lines = []

        for invoice_number, invoice_date in sorted(
            summary["invoice_records"]
        ):

            if not invoice_number:
                continue

            if invoice_date:

                invoice_lines.append(
                    f"{invoice_number} ({invoice_date})"
                )

            else:

                invoice_lines.append(
                    f"{invoice_number}"
                )

        bid_lines = []
        bid_lines = sorted(
            summary["bid_numbers"]
        )

        rows.append({

            "company":
                bidder,

            "purchaser":
                summary["purchaser_name"] or "",

            "po_invoice_details":
                (
                    "PO:\n"
                    + "\n".join(sorted(po_lines))
                    + "\n\nInvoice:\n"
                    + "\n".join(sorted(invoice_lines))
                ),
            "bid_numbers":
            "\n".join(bid_lines),

            "local_content":
                ", ".join(sorted(summary["local_content"])),

            "manual_review":
                "Yes" if summary["manual_review"] else "No",

            "review_location":
                (
                    f"{summary['pdf_number']} (Page {summary['page_number']})"
                    if summary["pdf_number"]
                    else ""
                )
        })

        serial_no += 1

    return rows