# Notes Helper – PDF Text Extraction, Summaries, and Keywords (Python/Flask)

Notes Helper is a lightweight Python/Flask application that converts PDF documents into structured notes.
It extracts full text, generates detailed summaries, identifies keywords, and allows exporting and managing processed notes.

Features

PDF Processing

- Extracts full text from multi-page PDFs

- Cleans PDF noise (HTML tags, CID artifacts, encoding issues)

- Normalizes spacing and formatting

Text Analysis

- Generates detailed extractive summaries

- Extracts keywords and important terms

- Cleans unwanted characters and noise before processing

Notes Management

- Saves notes including title, full text, summary, and keywords

- Search across:

  - Titles

  - Summaries

  - Full text

  - Keywords

- Delete individual notes

Interface

- Modern dark-themed UI

- Clear file selection indicator

- Tag-style keyword display

- Simple navigation and layout

Export Options

- Export processed notes as:

- TXT files

- PDF files (print-friendly format)

Technology Stack

- Backend: Python, Flask

- PDF Extraction: pdfplumber

- Text Processing: YAKE (keywords), custom summarizer

- Exporting: FPDF

- Storage: Local JSON file

- Frontend: HTML and CSS (dark theme)

