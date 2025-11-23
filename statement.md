# statement.md
## Notes Helper – PDF Text Extraction, Summaries, and Keyword Generation

### 1. Problem Statement
Students often receive long PDF notes and study materials that are difficult to manually read and process. Extracting important information such as summaries, keywords, and structured text from large PDFs is time-consuming and inefficient. There is a need for a tool that automates this process and helps students create concise and organized notes quickly.

### 2. Project Scope
Notes Helper is a local Python/Flask web application that allows users to upload PDF files and automatically generates:
- Clean and readable full text
- A detailed extractive summary
- Relevant keywords
- Exportable note formats (TXT and PDF)
- Tag-based keyword viewing
- A dark-themed user interface

The system stores notes locally in JSON, supports viewing, exporting, and deleting notes, and is designed as a single-user offline tool.

### 3. Target Users
- College students preparing for exams  
- Individuals working with large PDF documents  
- Users who require quick summaries and keyword extraction  
- Anyone needing organized, cleaned, and searchable notes

### 4. High-Level Features
- PDF upload and extraction  
- Cleaning of noisy text (CID artifacts, HTML tags, encoding issues)  
- Detailed extractive summarization  
- Keyword extraction using YAKE  
- Dark-mode interface  
- File-selection indicator  
- Local note saving (title, summary, text, keywords)  
- View notes with full details  
- Delete notes individually  
- Export notes as TXT  
- Export notes as PDF  

### 5. Out of Scope
- OCR for scanned/image-based PDFs  
- Multi-user login system  
- Cloud-based storage or syncing  
- AI-based abstractive summarization  
- Mobile/desktop application version  

These can be added as future enhancements.

### 6. Technology Used
- Python  
- Flask  
- pdfplumber (PDF extraction)  
- YAKE (keyword extraction)  
- FPDF (export as PDF)  
- HTML & CSS (frontend)  
- JSON (local storage)

### 7. Conclusion
Notes Helper provides an efficient way for students and professionals to convert lengthy PDFs into structured, readable notes. By automating extraction, summarization, and keyword generation, it significantly reduces manual effort and improves study productivity.
