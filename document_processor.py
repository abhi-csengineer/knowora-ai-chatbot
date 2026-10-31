
from pypdf import PdfReader


def extract_pages_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from every PDF page
    while preserving page numbers.
    """

    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page_number": page_number,
                "text": text.strip()
            })

    return pages


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[str]:
    """
    Split text into smaller overlapping chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and less than chunk_size."
        )

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks
