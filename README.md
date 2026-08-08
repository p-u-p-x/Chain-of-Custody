# Chain of Custody 🔗

![Python](https://img.shields.io/badge/Python-3776AB) ![Backboard](https://img.shields.io/badge/Backboard.io-1A237E) ![AI%20Agents](https://img.shields.io/badge/AI%20Agents-455A64) ![Multi%20Agent](https://img.shields.io/badge/Multi%20Agent-3F51B5) ![MLH](https://img.shields.io/badge/MLH%20GHW-E97627)

Built for MLH's Global Hack Week: Agents

A self correcting research pipeline made of three AI agents that check each other's work before a human ever sees the output.

## Table of Contents

* Overview
* How It Works
* Why Backboard
* Technical Implementation
* Setup
* Project Structure
* Demo
* Contact

## Overview

Chain of Custody takes a topic and produces a fact checked research brief with no human in the loop until the final, verified version lands. Three agents each own one job, and the third one is allowed to reject the second one's work and send it back.

## ⚙️ How It Works

Researcher gathers live sources from the web on the given topic and returns raw findings with citations, no analysis.

Synthesizer turns those raw findings into a structured, readable brief.

Critic compares the brief against the original research line by line. It rejects the brief if a claim isn't traceable to the source material, if a number or quote doesn't match exactly, if an interpretation is stated as fact without attribution, or if a real caveat from the research got dropped. If it rejects, the feedback goes back to the Synthesizer for a revision, up to three rounds.

```text
Topic → Researcher → Synthesizer → Critic
                          ↑             │
                          └─ feedback ──┘ (until approved, max 3 rounds)
```

## 🛹 Why Backboard

Each agent is a separate Backboard Assistant, its own system prompt, its own model, its own tools, so their reasoning stays isolated rather than blurring into one long prompt. Threads carry memory across the pipeline's steps without a hand rolled context store. The Researcher runs with Backboard's web search tool enabled so it pulls real current sources instead of relying on model memory. Model routing means the drafting steps can run on a lighter model while the final critique runs on a stronger one, without rewriting any integration code to swap them.

## Technical Implementation

```python
from backboard import BackboardClient
import asyncio

client = BackboardClient(api_key="YOUR_API_KEY")

async def create_agent(name, system_prompt):
    assistant = await client.create_assistant(
        name=name,
        system_prompt=system_prompt,
        llm_provider="anthropic",
        llm_model_name="claude-sonnet-4-6",
    )
    thread = await client.create_thread(assistant.assistant_id)
    return assistant, thread
```

The Critic's actual standard, this is the part that makes the loop real rather than decorative:

```python
CRITIC_PROMPT = (
    "You are a rigorous fact checking editor. Compare the brief line by line "
    "against the original research notes. Reject the brief if any claim isn't "
    "traceable to the notes, if a number, date, name, or quote doesn't match "
    "exactly, if an interpretation is stated as fact without attribution, or "
    "if a significant caveat from the notes was dropped. If you find an issue, "
    "list the specific problems and quote the sentence at fault. If and only "
    "if the brief passes every check, respond with exactly APPROVED."
)
```

## Setup

```bash
mkdir chain-of-custody && cd chain-of-custody
pip install backboard
export BACKBOARD_API_KEY="your_key_here"
python main.py
```

Every run saves the final, approved brief to a timestamped markdown file in the project folder.

## 📁 Project Structure

```text
chain-of-custody/
├── main.py            entry point, wires the three agents and the retry loop
├── agents.py          agent creation and prompts
├── requirements.txt
└── briefs/            timestamped output briefs land here
```

## 🎥 Demo

Video walkalong: [https://youtu.be/i43-8CPNaWE?si=WeOGo5M_zBdGwuZS]

---

## 📬 Contact

- ✉️ **Email:** [i.sajeela.noor@gmail.com](mailto:i.sajeela.noor@gmail.com)
- 💼 **LinkedIn:** [Sajeela Noor](https://www.linkedin.com/in/sajeela-noor-82b510256)
- 🐙 **GitHub:** [p-u-p-x](https://github.com/p-u-p-x)

