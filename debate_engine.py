"""
debate_engine.py
-----------------
Manages a multi-turn debate: given a topic, the user's stated stance/claim, and
the conversation history so far, generates the AI's next counterargument taking
the OPPOSING position. The AI always argues the opposite side of whatever the
user just said, functioning as a genuine devil's advocate/sparring partner.
"""

import anthropic


DEBATE_SYSTEM_TEMPLATE = """You are a skilled debate partner. The topic is: "{topic}"

Your role: argue AGAINST whatever position the user just stated, using strong, good-faith \
reasoning. You are not here to simply agree or validate - you are here to stress-test their \
argument with the strongest honest counterargument you can construct.

Rules:
- Directly engage with the user's specific claim and reasoning, don't just restate generic \
talking points.
- Use evidence-style reasoning (cite the KIND of evidence that would support your point, \
e.g. "studies on X tend to show...", without fabricating specific statistics or sources).
- Be respectful and substantive, not dismissive.
- Keep your response to 3-5 sentences - this is a back-and-forth debate, not an essay.
- If the user makes a genuinely strong point, you can acknowledge its strength before \
countering it - good debate doesn't ignore strong points.
"""


class DebateEngine:
    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def respond(self, topic: str, history: list[dict]) -> str:
        """
        history: list of {"role": "user"|"assistant", "content": str}, in order.
        Returns the AI's next counterargument as plain text.
        """
        system_prompt = DEBATE_SYSTEM_TEMPLATE.format(topic=topic)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            system=system_prompt,
            messages=history
        )
        return response.content[0].text.strip()


if __name__ == "__main__":
    engine = DebateEngine()
    topic = "Remote work is better for employee productivity than office work."
    history = [{"role": "user", "content": "Remote work eliminates commute time, so people have more energy and focus for actual work."}]

    reply = engine.respond(topic, history)
    print("AI:", reply)
