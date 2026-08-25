import os
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import AgentState
from graph.llm import get_llm


def _load_prompt() -> str:
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "understand.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return (
        "You are explaining a research paper section using first-principles reasoning and the Feynman technique.\n\n"
        "Source material:\n{sections}\n\n"
        "Task:\n"
        "1. Identify the core claim/method in plain language.\n"
        "2. Break it down to its most basic underlying truths — no jargon, no appeals to authority.\n"
        "3. Rebuild the explanation as if teaching a smart novice.\n"
        "4. Flag any part you could not simplify (a gap in understanding)."
    )


def _format_sections(sections: dict, raw_text: str) -> str:
    formatted_parts = []
    if sections:
        for key in ["abstract", "introduction", "method", "conclusion"]:
            if key in sections and sections[key]:
                formatted_parts.append(f"=== {key.upper()} ===\n{sections[key]}")
        if not formatted_parts:
            # Use core preview or first chunk of full_text
            preview = sections.get("core_preview") or sections.get("full_text", "")[:12000]
            formatted_parts.append(f"=== PAPER CONTENT ===\n{preview}")
    elif raw_text:
        formatted_parts.append(f"=== PAPER CONTENT ===\n{raw_text[:12000]}")
    else:
        formatted_parts.append("No text extracted.")

    return "\n\n".join(formatted_parts)


def understand_node(state: AgentState) -> AgentState:
    """
    Apply first-principles breakdown + Feynman technique to the paper's
    core method, using state['sections'] as source material.
    """
    sections = state.get("sections") or {}
    raw_text = state.get("raw_text") or ""
    source_material = _format_sections(sections, raw_text)

    prompt_template = _load_prompt()
    formatted_prompt = prompt_template.replace("{sections}", source_material)

    quiz_feedback = state.get("quiz_feedback")
    if quiz_feedback and state.get("attempt", 0) > 0:
        formatted_prompt += (
            f"\n\n[RETRY REFINEMENT - ADDRESS PREVIOUS GAPS]\n"
            f"The previous recall quiz indicated the following areas need better clarification:\n"
            f"{quiz_feedback}\n"
            f"Please ensure these gaps are thoroughly explained from first principles."
        )

    llm = get_llm(temperature=0.2)
    response = llm.invoke([
        SystemMessage(content="You are a world-class academic tutor using first-principles reasoning."),
        HumanMessage(content=formatted_prompt)
    ])

    raw_notes = response.content if hasattr(response, "content") else str(response)
    from graph.llm import clean_llm_output
    notes = clean_llm_output(raw_notes)
    return {**state, "understanding_notes": notes}


