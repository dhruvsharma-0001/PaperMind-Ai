from graph.state import AgentState
from tools.arxiv_fetcher import fetch_arxiv_pdf
from tools.pdf_parser import parse_pdf_text


def ingest_node(state: AgentState) -> AgentState:
    """Fetch the paper or use uploaded PDF bytes, and extract raw text + a section map."""
    pdf_bytes = state.get("pdf_bytes")
    
    if not pdf_bytes:
        paper_url = state.get("paper_url")
        if not paper_url:
            raise ValueError("Either 'paper_url' or 'pdf_bytes' must be provided.")
        pdf_bytes = fetch_arxiv_pdf(paper_url)

    raw_text, sections = parse_pdf_text(pdf_bytes)
    return {**state, "raw_text": raw_text, "sections": sections}

