import re
import requests


def normalize_arxiv_url(input_str: str) -> str:
    """Extract arXiv ID and format canonical PDF download URL."""
    input_str = input_str.strip()
    
    # Match arxiv IDs like 1706.03762, 1706.03762v2, cs/0101001, etc.
    arxiv_pattern = r"(?:arxiv\.org/(?:abs|pdf|html)/|arxiv:)?([a-zA-Z\-]+/\d{7}|\d{4}\.\d{4,5}(?:v\d+)?)"
    match = re.search(arxiv_pattern, input_str, re.IGNORECASE)
    
    if match:
        arxiv_id = match.group(1)
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    if input_str.startswith("http://") or input_str.startswith("https://"):
        # If it is already a direct URL
        if not input_str.endswith(".pdf"):
            return input_str.replace("/abs/", "/pdf/").replace("/html/", "/pdf/") + ".pdf"
        return input_str
        
    return f"https://arxiv.org/pdf/{input_str}.pdf"


def fetch_arxiv_pdf(paper_url: str) -> bytes:
    """Download PDF bytes from an arXiv URL or identifier."""
    pdf_url = normalize_arxiv_url(paper_url)
    headers = {
        "User-Agent": "PaperMindAI/1.0 (Autonomous research assistant; mailto:contact@example.com)"
    }

    
    try:
        resp = requests.get(pdf_url, headers=headers, timeout=45)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch arXiv PDF from '{pdf_url}': {str(e)}") from e

