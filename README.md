# Tender Document Field Extraction Pipeline

## Overview

This project automates the extraction of key information from tender-related PDF documents and generates a structured summary for further review.

The workflow combines **Python** for document processing and **UiPath** for orchestration and Excel automation.

## Features

* Processes all PDF documents inside bidder folders
* Automatically detects digital and scanned PDFs
* OCR support for scanned documents using EasyOCR
* Extracts:
  * Purchaser name
  * Purchase Order (PO) Number and Date
  * Invoice Number and Date
  * Bid Number
  * Local Content Percentage
* Flags documents requiring manual review
* Generates a consolidated CSV summary
* Populates the required Excel template through UiPath
* Moves processed folders after successful execution



## Project Structure

project/
│
├── Input/
│   ├── Bidder1/
│   ├── Bidder2/
│   └── ...
│
├── Output/
│   └── summary_output.csv
│
├── Processed/
|
│
├── src/
│   ├── aggregator.py
│   ├── extractor.py
│   └── ocr.py
│
├── main.py
├── requirements.txt
└── README.md

## Requirements

* Python 3.11 or later
* Poppler for Windows
* UiPath Studio (for RPA workflow)

Install Python packages:

pip install -r requirements.txt


### Poppler Installation

Download Poppler for Windows:

https://github.com/oschwartz10612/poppler-windows/releases

Extract the archive and add:

<Poppler>\Library\bin

to the Windows PATH environment variable.

## Output

The Python pipeline generates:

Output/summary_output.csv

The CSV contains:

* Company
* Purchaser
* PO & Invoice Details
* Bid Number
* Local Content
* Manual Review Status
* Review Location

UiPath reads this CSV and writes the extracted information into the required Excel template.

## Workflow

Input Folder
      │
      ▼
UiPath Trigger
      │
      ▼
Python Processing
      │
 ├── Digital PDF Extraction
 ├── OCR (Scanned PDFs)
 ├── Information Extraction
 ├── Data Aggregation
 └── CSV Generation
      │
      ▼
UiPath
      │
 ├── Read CSV
 ├── Populate Excel
 └── Move Processed Folder

## Notes

* OCR is performed only on scanned pages.
* Duplicate PO, Invoice and Bid records are automatically removed.
* Documents with poor OCR quality are marked for manual review.
* The project is modular, allowing extraction rules to be extended easily.


## Challenges Encountered

During development, several practical challenges that I encountered were:

* Tender documents were not standardized, requiring flexible extraction logic.
* Scanned PDFs required OCR processing, while digital PDFs used direct text extraction.
* OCR quality varied significantly depending on scan resolution and document quality.
* Maintaining the association between Purchase Orders, Invoices and Bid Numbers required careful aggregation and duplicate removal.
* Integrating Python document processing with UiPath orchestration required a well-defined interface using CSV output.
* Multiple iterations of regular expression tuning were required to improve extraction accuracy across different document layouts.
* Balancing automation with reliability led to the inclusion of manual review flags for low-confidence or incomplete extractions.

## Future Improvements

The current implementation serves as a functional prototype. The following enhancements can be considered in future versions:

* Improve purchaser name extraction using context-aware parsing instead of regex-based extraction.
* Improve performance of processing pipeline by enabling gpu accelaration.
* Support additional tender document formats and layouts.
* Improve OCR accuracy through image preprocessing techniques.
* Add logging for easier debugging.
* Generate Excel reports directly from Python as an alternative to CSV.
* Implement exception handling and recovery mechanisms.
* Add support for concurrent processing of multiple bidder folders to improve performance.
* Implement confidence scores for extracted fields to assist manual verification.
