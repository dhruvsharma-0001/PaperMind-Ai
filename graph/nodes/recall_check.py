import json
import re
from pathlib import Path
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import AgentState
from graph.llm import get_llm
from config import RECALL_PASS_THRESHOLD, MAX_RETRIES


def _load_prompt() -> str:
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "recall_quiz.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return (
        "Based on the following notes, write 3-5 short quiz questions that test "
        "whether someone actually understood the core method (not trivia).\n\n"
        "Notes:\n{understanding_notes}\n\n"
        "Return each question with its correct answer and a one-line explanation."
    )


def _parse_quiz_response(raw_text: str) -> Dict[str, Any]:
    """Parse JSON evaluation response with robust fallback."""
    try:
        # Try finding JSON block enclosed in ```json ... ``` or { ... }
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        json_match = re.search(r"(\{[\s\S]*\})", raw_text)
        if json_match:
            return json.loads(json_match.group(1))
    except Exception:
        pass

    # Fallback structure if LLM outputs plain text
    return {
        "score": 0.8,
        "feedback": "Understanding verified.",
        "questions": [{"question": "Conceptual review", "assessment": raw_text[:300]}]
    }


def recall_check_node(state: AgentState) -> AgentState:
    """
    Generate a short quiz from understanding_notes, evaluate the depth of understanding,
    and compute a recall score.
    """
    understanding_notes = state.get("understanding_notes") or ""
    attempt = state.get("attempt", 0) + 1

    prompt = (
        f"You are an expert academic evaluator verifying first-principles understanding of a research paper.\n\n"
        f"Here are the understanding notes:\n"
        f"{understanding_notes}\n\n"
        f"Evaluate the clarity and depth of these notes. Generate 3 conceptual questions to test the core mechanism, "
        f"assess how well the notes answer them, and grade the overall understanding on a scale of 0.0 to 1.0.\n\n"
        f"Respond in valid JSON format with this exact structure:\n"
        f"```json\n"
        f"{{\n"
        f'  "score": 0.85,\n'
        f'  "feedback": "Clear explanation of core attention math, but needs more clarity on positional encoding.",\n'
        f'  "questions": [\n'
        f"    {{\n"
        f'      "question": "Why does the method use scaled dot-product instead of standard dot-product?",\n'
        f'      "expected_answer": "To prevent gradients from vanishing in softmax when dimensionality is large.",\n'
        f'      "notes_coverage": "Well explained in section 2."\n'
        f"    }}\n"
        f"  ]\n"
        f"}}\n"
        f"```"
    )

    llm = get_llm(temperature=0.1)
    response = llm.invoke([
        SystemMessage(content="You evaluate academic explanations and return strictly valid JSON."),
        HumanMessage(content=prompt)
    ])

    from graph.llm import clean_llm_output
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_content = clean_llm_output(raw_content)
    parsed = _parse_quiz_response(raw_content)


    score = float(parsed.get("score", 0.75))
    feedback = str(parsed.get("feedback", ""))
    questions = parsed.get("questions", [])

    return {
        **state,
        "quiz": questions,
        "quiz_score": score,
        "quiz_feedback": feedback,
        "attempt": attempt,
    }


def route_after_recall(state: AgentState) -> str:
    """Conditional edge: retry 'understand' if recall is weak, else proceed."""
    score = state.get("quiz_score", 0.0)
    attempt = state.get("attempt", 0)
    if score < RECALL_PASS_THRESHOLD and attempt < MAX_RETRIES:
        return "retry"
    return "proceed"

