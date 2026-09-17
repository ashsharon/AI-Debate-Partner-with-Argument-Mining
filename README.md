# AI Debate Partner with Argument Mining

A debate practice tool where the AI always argues the opposing side of whatever you
say - and, uniquely, mines the argumentative structure (claim, warrant, stance) of
every turn as the debate happens, rendering it live as a graph of who's rebutting whom.

**This is the unique feature relative to typical debate chatbots:** most just generate
back-and-forth text. This one combines generation with argument mining and graph
visualization, so you can literally see the shape of the debate, not just read it.

## Architecture

```
User states a claim
        │
        ▼
argument_miner.py  ──► extracts {claim, warrant, stance} from user's turn
        │
        ▼
debate_engine.py     ──► LLM generates a counterargument (always opposing side)
        │
        ▼
argument_miner.py       ──► extracts {claim, warrant, stance} from AI's turn,
        │                     linked as a rebuttal to the user's turn
        ▼
graph_builder.py           ──► converts all mined nodes into a Graphviz DOT graph
        │
        ▼
pipeline.py (DebateSession)  ──► maintains full session state across turns
        │
        ▼
app.py                          ──► Streamlit chat UI + live graph rendering
```

## Project structure

```
ai-debate-partner/
├── app.py                    # Streamlit frontend (chat + graph)
├── pipeline.py                 # DebateSession: orchestrates state across turns
├── debate_engine.py              # LLM counterargument generation
├── argument_miner.py               # LLM structure extraction (claim/warrant/stance)
├── graph_builder.py                  # Builds Graphviz DOT string from mined nodes
├── requirements.txt
├── .env.example
└── data/
    └── sample_topics.json              # 5 sample debate topics
```

## Setup (VS Code / local)

1. **Open this folder in VS Code.**

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY=your-key-here     # macOS/Linux
   set ANTHROPIC_API_KEY=your-key-here        # Windows (cmd)
   ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   Pick a sample topic (or write your own), state your opening argument in the chat
   box, and watch the AI counter it while the argument graph builds below the chat.

6. **Or run from the command line** (single exchange, prints the graph DOT source):
   ```bash
   python pipeline.py
   ```

## Testing individual components

```bash
python debate_engine.py     # test counterargument generation alone
python argument_miner.py      # test structure extraction on one turn
python graph_builder.py         # test DOT graph generation from sample nodes
```

## Extending it (ideas for your report / future work section)

- Support multi-party debates (3+ participants) instead of strictly 1-vs-1.
- Add a "steelman mode" where the AI first restates your argument in its strongest
  form before countering it, to study argument quality separately from rebuttal.
- Score argument strength per turn (e.g. via a rubric-prompted LLM judge) and overlay
  scores on the graph nodes.
- Export the mined argument graph as structured data (JSON) for corpus-level analysis
  across many debate sessions, useful if you want a quantitative evaluation section.
- Compare against a classical argument-mining pipeline (e.g. rule-based or a trained
  sequence-tagging model) as a baseline to discuss LLM-based mining accuracy/limits.

## Notes

- Graph rendering uses Streamlit's built-in `st.graphviz_chart`, so no extra JS
  visualization library is needed - keeps setup dependency-light.
- Each turn requires 3 LLM calls (mine user turn, generate AI reply, mine AI turn) -
  worth noting if you're tracking API cost/latency for your methodology section.
