from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict, total=False):
    """Shared state passed between every node in the graph."""

    paper_url: Optional[str]
    pdf_bytes: Optional[bytes]
    filename: Optional[str]
    raw_text: Optional[str]
    sections: Optional[Dict[str, Any]]


    understanding_notes: Optional[str]

    quiz: Optional[List[Dict[str, Any]]]
    quiz_score: Optional[float]
    quiz_feedback: Optional[str]
    attempt: int

    output: Optional[str]
    error: Optional[str]

