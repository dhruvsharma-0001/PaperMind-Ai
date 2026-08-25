from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import AgentState
from graph.llm import get_llm


def _load_prompt() -> str:
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "teach_back.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return (
        "Based on these understanding notes, produce:\n"
        "1. A clean, commented Python code sketch reimplementing the core method/algorithm from scratch (e.g. using PyTorch or pure NumPy/Python).\n"
        "2. A 3-5 sentence teach-back summary, explaining the core intuition simply as if to a peer engineer.\n\n"
        "Notes:\n{understanding_notes}\n"
    )


def apply_node(state: AgentState) -> AgentState:
    """
    Reimplement the core method (code sketch) and produce a teach-back
    summary from state['understanding_notes'].
    """
    understanding_notes = state.get("understanding_notes") or ""
    prompt_template = _load_prompt()
    formatted_prompt = prompt_template.replace("{understanding_notes}", understanding_notes)

    llm = get_llm(temperature=0.2)
    response = llm.invoke([
        SystemMessage(content="You are an expert engineer and research mentor who writes clean, educational reference code."),
        HumanMessage(content=formatted_prompt)
    ])

    from graph.llm import clean_llm_output
    raw_output = response.content if hasattr(response, "content") else str(response)
    output = clean_llm_output(raw_output)
    return {**state, "output": output}


