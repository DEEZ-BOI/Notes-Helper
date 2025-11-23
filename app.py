from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import json
import re
from collections import Counter

import pdfplumber
import yake
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
NOTES_FILE = "notes.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- Notes storage helpers ---------- #

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


# ---------- Text utilities ---------- #

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then",
    "of", "on", "in", "to", "for", "by", "is", "are",
    "was", "were", "be", "being", "been", "as", "at",
    "that", "this", "with", "from", "it", "its", "they",
    "them", "their", "we", "our", "you", "your", "i", "me",
    "he", "she", "his", "her", "not", "no", "so", "such",
    "can", "may", "will", "would", "could", "should",
    "have", "has", "had", "do", "does", "did", "about",
    "into", "over", "also", "than", "there", "here"
}


def clean_text(text: str) -> str:
    """Clean noisy PDF text (tags, cid junk, extra spaces)."""
    if not text:
        return ""

    # remove tags like <b>, <i>, <br>, etc.
    text = re.sub(r"<[^>]+>", " ", text)

    # remove cid-style garbage: cid0, cid:123, CID-14, etc.
    text = re.sub(r"\bcid[:\-]?\d*\b", " ", text, flags=re.IGNORECASE)

    # sometimes just 'cid' alone appears; kill it too
    text = re.sub(r"\bcid\b", " ", text, flags=re.IGNORECASE)

    # remove weird NULLs and control chars
    text = text.replace("\x00", " ")

    # collapse multiple spaces/newlines
    text = re.sub(r"\s+", " ", text)

    return text.strip()



def extract_pdf_text(path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            parts.append(txt)
    return clean_text("\n\n".join(parts))


def detailed_summary(text: str, max_sentences: int = 8) -> str:
    """
    Slightly smarter extractive summary:
    - split into sentences
    - score sentences by word frequency
    - pick top N sentences in original order
    """
    text = clean_text(text)
    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # word frequency
    words = re.findall(r"\w+", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS)

    scores = []
    for sent in sentences:
        tokens = re.findall(r"\w+", sent.lower())
        score = sum(freq.get(w, 0) for w in tokens)
        scores.append(score)

    # pick top N by score, but keep original order
    ranked_indices = sorted(range(len(sentences)),
                            key=lambda i: scores[i],
                            reverse=True)
    chosen_idx = sorted(ranked_indices[:max_sentences])
    return " ".join(sentences[i] for i in chosen_idx)


def extract_keywords(text: str, top_k: int = 12):
    text = clean_text(text)
    if not text:
        return []
    kw_extractor = yake.KeywordExtractor()
    kws = kw_extractor.extract_keywords(text)
    return [word for (word, score) in kws[:top_k]]


def safe_filename(title: str, ext: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9_-]+", "_", title)
    if not base:
        base = "note"
    return f"{base}.{ext}"


# ---------- Routes ---------- #

@app.route("/", methods=["GET", "POST"])
def index():
    notes = load_notes()

    if request.method == "POST":
        pdf_file = request.files.get("pdf")
        if not pdf_file or pdf_file.filename == "":
            return "No file selected", 400

        save_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        pdf_file.save(save_path)

        full_text = extract_pdf_text(save_path)
        summary = detailed_summary(full_text, max_sentences=8)
        keywords = extract_keywords(full_text)

        note = {
            "title": pdf_file.filename,
            "text": full_text,
            "summary": summary,
            "keywords": keywords,
            "filename": pdf_file.filename,
        }
        notes.append(note)
        save_notes(notes)

        return redirect(url_for("index"))

    return render_template("index.html", notes=notes)


@app.route("/view/<int:note_id>")
def view_note(note_id):
    notes = load_notes()
    if 0 <= note_id < len(notes):
        return render_template(
            "view.html",
            note=notes[note_id],
            note_id=note_id
        )
    return "Note not found", 404


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    notes = load_notes()
    if 0 <= note_id < len(notes):
        notes.pop(note_id)
        save_notes(notes)
    return redirect(url_for("index"))


@app.route("/export/<int:note_id>/txt")
def export_txt(note_id):
    notes = load_notes()
    if not (0 <= note_id < len(notes)):
        return "Note not found", 404

    note = notes[note_id]
    content = (
        f"Title: {note['title']}\n\n"
        f"Keywords: {', '.join(note.get('keywords', []))}\n\n"
        f"SUMMARY:\n{note.get('summary', '')}\n\n"
        f"FULL TEXT:\n{note.get('text', '')}\n"
    )

    filename = safe_filename(note["title"], "txt")
    resp = make_response(content)
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return resp


@app.route("/export/<int:note_id>/pdf")
def export_pdf(note_id):
    notes = load_notes()
    if not (0 <= note_id < len(notes)):
        return "Note not found", 404

    note = notes[note_id]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.multi_cell(0, 8, note["title"])
    pdf.ln(4)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, "Keywords: " + ", ".join(note.get("keywords", [])))
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(0, 6, "Summary:")
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 5, note.get("summary", ""))
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(0, 6, "Full Text:")
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 5, note.get("text", ""))

    pdf_bytes = pdf.output(dest="S").encode("latin-1", "ignore")
    filename = safe_filename(note["title"], "pdf")

    resp = make_response(pdf_bytes)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return resp


if __name__ == "__main__":
    app.run(debug=True)
