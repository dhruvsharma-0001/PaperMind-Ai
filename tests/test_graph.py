from unittest.mock import patch, MagicMock
from graph.builder import build_graph
from graph.nodes.recall_check import route_after_recall, _parse_quiz_response
from tools.arxiv_fetcher import normalize_arxiv_url
from tools.pdf_parser import clean_text, parse_pdf_text


def test_graph_compiles():
    agent = build_graph()
    assert agent is not None


def test_arxiv_url_normalization():
    assert normalize_arxiv_url("1706.03762") == "https://arxiv.org/pdf/1706.03762.pdf"
    assert normalize_arxiv_url("https://arxiv.org/abs/1706.03762") == "https://arxiv.org/pdf/1706.03762.pdf"
    assert normalize_arxiv_url("https://arxiv.org/pdf/1706.03762.pdf") == "https://arxiv.org/pdf/1706.03762.pdf"
    assert normalize_arxiv_url("https://arxiv.org/html/2301.07041v1") == "https://arxiv.org/pdf/2301.07041v1.pdf"


def test_recall_routing():
    # Attempt 1, low score -> retry
    assert route_after_recall({"quiz_score": 0.5, "attempt": 1}) == "retry"
    # Attempt 1, passing score -> proceed
    assert route_after_recall({"quiz_score": 0.8, "attempt": 1}) == "proceed"
    # Attempt 3 (max retries reached), low score -> proceed (avoid infinite loop)
    assert route_after_recall({"quiz_score": 0.5, "attempt": 3}) == "proceed"


def test_quiz_json_parsing():
    valid_json = '```json\n{"score": 0.9, "feedback": "Great", "questions": []}\n```'
    parsed = _parse_quiz_response(valid_json)
    assert parsed["score"] == 0.9
    assert parsed["feedback"] == "Great"

    fallback = _parse_quiz_response("Not a JSON response")
    assert "score" in fallback


def test_clean_text():
    dirty = "Hello   world \x00\r\n\n\nNew paragraph"
    cleaned = clean_text(dirty)
    assert "\x00" not in cleaned
    assert "\r" not in cleaned
    assert "Hello world" in cleaned


@patch("graph.nodes.ingest.fetch_arxiv_pdf")
@patch("graph.nodes.ingest.parse_pdf_text")
@patch("graph.nodes.understand.get_llm")
@patch("graph.nodes.recall_check.get_llm")
@patch("graph.nodes.apply.get_llm")
def test_full_graph_mocked_execution(mock_apply_llm, mock_recall_llm, mock_understand_llm, mock_parse_pdf, mock_fetch_pdf):
    # Mock PDF download and parsing
    mock_fetch_pdf.return_value = b"%PDF-mock"
    mock_parse_pdf.return_value = ("Full paper text about Attention", {"abstract": "Attention is all you need"})

    # Mock Understand LLM
    understand_llm = MagicMock()
    understand_llm.invoke.return_value = MagicMock(content="First-principles breakdown: Attention calculates weighted values based on query-key similarity.")
    mock_understand_llm.return_value = understand_llm

    # Mock Recall LLM
    recall_llm = MagicMock()
    recall_llm.invoke.return_value = MagicMock(content='```json\n{"score": 0.85, "feedback": "Good understanding", "questions": [{"question": "Why scale?", "expected_answer": "Grad stability"}]}\n```')
    mock_recall_llm.return_value = recall_llm

    # Mock Apply LLM
    apply_llm = MagicMock()
    apply_llm.invoke.return_value = MagicMock(content="```python\ndef attention(q, k, v):\n    return softmax(q @ k.T) @ v\n```\n\nTeach-back: Attention routes information dynamically.")
    mock_apply_llm.return_value = apply_llm

    agent = build_graph()
    initial_state = {"paper_url": "1706.03762", "attempt": 0}
    result = agent.invoke(initial_state)

    assert result["paper_url"] == "1706.03762"
    assert "understanding_notes" in result
    assert result["quiz_score"] == 0.85
    assert "output" in result
    assert "def attention" in result["output"]


@patch("graph.nodes.ingest.fetch_arxiv_pdf")
@patch("graph.nodes.ingest.parse_pdf_text")
@patch("graph.nodes.understand.get_llm")
@patch("graph.nodes.recall_check.get_llm")
@patch("graph.nodes.apply.get_llm")
def test_retry_loop_execution(mock_apply_llm, mock_recall_llm, mock_understand_llm, mock_parse_pdf, mock_fetch_pdf):
    mock_fetch_pdf.return_value = b"%PDF-mock"
    mock_parse_pdf.return_value = ("Sample paper", {"abstract": "Abstract text"})

    # 1st understand call, 2nd understand call
    understand_llm = MagicMock()
    understand_llm.invoke.side_effect = [
        MagicMock(content="First shallow attempt."),
        MagicMock(content="Second refined first-principles explanation addressing feedback.")
    ]
    mock_understand_llm.return_value = understand_llm

    # 1st recall (fails with 0.4), 2nd recall (passes with 0.9)
    recall_llm = MagicMock()
    recall_llm.invoke.side_effect = [
        MagicMock(content='```json\n{"score": 0.4, "feedback": "Too shallow on math", "questions": []}\n```'),
        MagicMock(content='```json\n{"score": 0.9, "feedback": "Greatly improved", "questions": []}\n```'),
    ]
    mock_recall_llm.return_value = recall_llm

    apply_llm = MagicMock()
    apply_llm.invoke.return_value = MagicMock(content="Code and teach-back output.")
    mock_apply_llm.return_value = apply_llm

    agent = build_graph()
    initial_state = {"paper_url": "https://arxiv.org/abs/1706.03762", "attempt": 0}
    result = agent.invoke(initial_state)

    # Verifications
    assert result["attempt"] == 2
    assert result["quiz_score"] == 0.9
    assert "Second refined" in result["understanding_notes"]
    assert mock_understand_llm.return_value.invoke.call_count == 2
    assert mock_recall_llm.return_value.invoke.call_count == 2


@patch("graph.nodes.ingest.parse_pdf_text")
@patch("graph.nodes.understand.get_llm")
@patch("graph.nodes.recall_check.get_llm")
@patch("graph.nodes.apply.get_llm")
def test_direct_pdf_upload_execution(mock_apply_llm, mock_recall_llm, mock_understand_llm, mock_parse_pdf):
    # Tests that when pdf_bytes is supplied, fetch_arxiv_pdf is NOT called
    mock_parse_pdf.return_value = ("Uploaded paper text", {"method": "Uploaded method"})

    understand_llm = MagicMock()
    understand_llm.invoke.return_value = MagicMock(content="First-principles breakdown of uploaded PDF.")
    mock_understand_llm.return_value = understand_llm

    recall_llm = MagicMock()
    recall_llm.invoke.return_value = MagicMock(content='```json\n{"score": 0.95, "feedback": "Excellent", "questions": []}\n```')
    mock_recall_llm.return_value = recall_llm

    apply_llm = MagicMock()
    apply_llm.invoke.return_value = MagicMock(content="Code from uploaded PDF.")
    mock_apply_llm.return_value = apply_llm

    agent = build_graph()
    custom_pdf_bytes = b"%PDF-1.4 custom test bytes"
    initial_state = {"pdf_bytes": custom_pdf_bytes, "filename": "my_research.pdf", "attempt": 0}
    result = agent.invoke(initial_state)

    assert result["filename"] == "my_research.pdf"
    assert result["quiz_score"] == 0.95
    assert "uploaded PDF" in result["understanding_notes"]
    assert "Code from uploaded PDF" in result["output"]





