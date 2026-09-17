"""
pipeline.py
-----------
Top-level orchestration: maintains debate state (topic, conversation history,
mined argument nodes) and exposes a single method to process one user turn:
1. Mine the structure of the user's turn (claim/warrant/stance)
2. Generate the AI's counterargument
3. Mine the structure of the AI's turn, linked as a rebuttal to the user's turn
4. Return the updated graph (DOT string) alongside the AI's reply text
"""

from debate_engine import DebateEngine
from argument_miner import ArgumentMiner
from graph_builder import build_dot_graph


class DebateSession:
    def __init__(self, topic: str, api_key: str | None = None):
        self.topic = topic
        self.history = []          # list of {"role", "content"} for the LLM conversation
        self.nodes = []             # list of mined argument nodes for the graph
        self.turn_counter = 0

        self.debate_engine = DebateEngine(api_key=api_key)
        self.miner = ArgumentMiner(api_key=api_key)

    def submit_user_turn(self, user_text: str) -> dict:
        """
        Processes one full exchange: user's argument -> AI's counterargument.
        Returns {"ai_reply": str, "graph_dot": str, "nodes": list}.
        """
        self.turn_counter += 1
        user_node_id = f"turn_{self.turn_counter}_user"

        user_structure = self.miner.mine_turn(self.topic, user_text)
        self.nodes.append({
            "id": user_node_id,
            "claim": user_structure["claim"],
            "warrant": user_structure["warrant"],
            "stance": user_structure["stance"],
            "speaker": "user",
            "rebuts": self._last_ai_node_id()
        })

        self.history.append({"role": "user", "content": user_text})
        ai_reply = self.debate_engine.respond(self.topic, self.history)
        self.history.append({"role": "assistant", "content": ai_reply})

        ai_node_id = f"turn_{self.turn_counter}_ai"
        ai_structure = self.miner.mine_turn(self.topic, ai_reply)
        self.nodes.append({
            "id": ai_node_id,
            "claim": ai_structure["claim"],
            "warrant": ai_structure["warrant"],
            "stance": ai_structure["stance"],
            "speaker": "ai",
            "rebuts": user_node_id
        })

        return {
            "ai_reply": ai_reply,
            "graph_dot": build_dot_graph(self.nodes),
            "nodes": self.nodes
        }

    def _last_ai_node_id(self):
        ai_nodes = [n for n in self.nodes if n["speaker"] == "ai"]
        return ai_nodes[-1]["id"] if ai_nodes else None


if __name__ == "__main__":
    session = DebateSession("Remote work is better for employee productivity than office work.")
    result = session.submit_user_turn(
        "Remote work eliminates commute time, so people have more energy and focus for actual work."
    )
    print("AI reply:", result["ai_reply"])
    print("\nGraph DOT:\n", result["graph_dot"])
