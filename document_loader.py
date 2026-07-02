"""
document_loader.py
Handles loading raw text out of PDFs, DOCX, and TXT files,
and splitting that text into overlapping chunks for embedding.
"""

import os
from typing import List, Dict
from pypdf import PdfReader
import docx


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text.append(page_text)
    return "\n".join(text)


def load_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf(path)
    elif ext == ".docx":
        return load_docx(path)
    elif ext == ".txt":
        return load_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Simple sliding-window chunking by characters.
    chunk_size and overlap are in characters, not tokens, to keep this
    dependency-free and predictable.
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        # try to break on a sentence/paragraph boundary near the end
        boundary = text.rfind(". ", start, end)
        if boundary != -1 and boundary > start + chunk_size * 0.5:
            end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break
        start = end - overlap

    return chunks


def load_and_chunk_folder(folder_path: str, chunk_size: int = 800, overlap: int = 150) -> List[Dict]:
    """
    Walks a folder, loads every supported document, and returns a list of
    dicts: {"text": chunk, "source": filename, "chunk_id": index}
    """
    all_chunks = []
    supported_ext = {".pdf", ".docx", ".txt"}

    for fname in sorted(os.listdir(folder_path)):
        fpath = os.path.join(folder_path, fname)
        ext = os.path.splitext(fname)[1].lower()
        if not os.path.isfile(fpath) or ext not in supported_ext:
            continue

        try:
            raw_text = load_document(fpath)
        except Exception as e:
            print(f"Skipping {fname}: {e}")
            continue

        chunks = chunk_text(raw_text, chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": fname,
                "chunk_id": i
            })

    return all_chunks
