"""
graph_builder.py
-----------------
Converts the sequence of mined argument nodes (each with claim, warrant, stance,
and a "rebuts" link to the previous node) into a Graphviz DOT string.

Streamlit can render Graphviz DOT natively via st.graphviz_chart, so this keeps
the visualization dependency-light (no extra JS libraries needed).
"""


def _wrap_label(text: str, width: int = 30) -> str:
    """Simple word-wrap for node labels so long claims don't render as one huge line."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return "\\n".join(lines)


def build_dot_graph(nodes: list[dict]) -> str:
    """
    nodes: list of dicts, each with:
        - id: str (unique, e.g. "turn_1")
        - claim: str
        - warrant: str
        - stance: "supports_topic" | "opposes_topic"
        - speaker: "user" | "ai"
        - rebuts: str | None (id of the node this one argues against)
    """
    lines = ["digraph ArgumentGraph {", '  rankdir="TB";', '  node [shape=box, style="rounded,filled", fontname="Helvetica"];']

    for node in nodes:
        color = "#DCEEFB" if node["stance"] == "supports_topic" else "#FBE0E0"
        speaker_tag = "You" if node["speaker"] == "user" else "AI"
        label = f"{speaker_tag}: {_wrap_label(node['claim'])}"
        if node.get("warrant"):
            label += f"\\n\\n(because: {_wrap_label(node['warrant'], width=28)})"

        lines.append(f'  "{node["id"]}" [label="{label}", fillcolor="{color}"];')

    for node in nodes:
        if node.get("rebuts"):
            lines.append(f'  "{node["rebuts"]}" -> "{node["id"]}" [label="rebuts", color="#888888"];')

    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    sample_nodes = [
        {"id": "turn_1", "claim": "Remote work boosts productivity by removing commute time.",
         "warrant": "Saved time and energy goes toward actual work.", "stance": "supports_topic",
         "speaker": "user", "rebuts": None},
        {"id": "turn_2", "claim": "Removed commute time doesn't guarantee more focused work.",
         "warrant": "Home environments introduce different distractions.", "stance": "opposes_topic",
         "speaker": "ai", "rebuts": "turn_1"},
    ]
    print(build_dot_graph(sample_nodes))
