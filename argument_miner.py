"""
argument_miner.py
------------------
Extracts the argumentative STRUCTURE of a debate turn: the claim being made,
the warrant (reasoning/evidence backing it), and - if this turn rebuts a prior
turn - which prior claim it's rebutting.

This turns unstructured back-and-forth debate text into a graph of
claims/warrants/rebuttals that can be visualized, which is the unique feature
of this project (most debate-bots just generate text with no structure).
"""

import json
import anthropic


MINING_SYSTEM_PROMPT = """You are an argument mining system. Given ONE turn of a debate \
(a single claim/argument someone just made) and optionally the ID of the argument it \
responds to, extract its structure.

Respond ONLY with valid JSON, no markdown fences, in this exact shape:
{
  "claim": "the core claim being made, in one concise sentence",
  "warrant": "the reasoning or evidence given to support the claim, in one concise sentence",
  "stance": "supports_topic" | "opposes_topic"
}

Rules:
- "claim" should be the central assertion, not a restatement of the whole turn.
- "warrant" should be the WHY behind the claim - the reasoning offered.
- "stance" reflects whether this turn argues FOR or AGAINST the original debate topic \
overall (not just the immediately preceding turn).
"""


class ArgumentMiner:
    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def mine_turn(self, topic: str, turn_text: str) -> dict:
        user_message = f"DEBATE TOPIC: {topic}\n\nTURN TEXT: {turn_text}"

        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            system=MINING_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )

        raw = response.content[0].text.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"claim": turn_text[:80], "warrant": "", "stance": "unclear"}


if __name__ == "__main__":
    miner = ArgumentMiner()
    topic = "Remote work is better for employee productivity than office work."
    turn = "Remote work eliminates commute time, so people have more energy and focus for actual work."

    result = miner.mine_turn(topic, turn)
    print(json.dumps(result, indent=2))
