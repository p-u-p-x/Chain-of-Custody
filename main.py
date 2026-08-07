import asyncio
import os
from dotenv import load_dotenv
from backboard import BackboardClient
from datetime import datetime

load_dotenv()

client = BackboardClient(api_key=os.getenv("BACKBOARD_API_KEY"), timeout=180)

MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-haiku-4-5-20251001"
MAX_RETRIES = 3


def get_reply(response) -> str:
    """Pull the assistant's reply text out of a send_message response."""
    return response.messages[-1]["content"]


async def create_agent(name: str, system_prompt: str):
    assistant = await client.create_assistant(
        name=name,
        system_prompt=system_prompt,
    )
    thread = await client.create_thread(assistant.assistant_id)
    return assistant, thread


async def main():
    topic = input("What topic should the pipeline research? ")

    researcher, researcher_thread = await create_agent(
        "Researcher",
        "You research topics using web search. Return raw findings "
        "with sources, no analysis or opinions.",
    )
    synthesizer, synthesizer_thread = await create_agent(
        "Synthesizer",
        "You take raw research notes and write a clear, structured "
        "brief with headers, bullet points, and inline source citations.",
    )
    critic, critic_thread = await create_agent(
        "Critic",
        "You are a rigorous fact-checking editor. Compare the brief line by line "
        "against the original research notes. Reject the brief (do not respond "
        "APPROVED) if ANY of the following are true: "
        "(1) a claim in the brief is not directly traceable to something stated "
        "in the research notes, "
        "(2) a specific number, date, name, or quote in the brief doesn't exactly "
        "match the research notes, "
        "(3) the brief states a scholarly interpretation or opinion as if it were "
        "an established fact, without attributing it, "
        "(4) the brief omits a significant caveat or counterpoint that was present "
        "in the research notes. "
        "If you find any issue, respond with a numbered list of the specific "
        "problems, quoting the exact sentence in the brief that's at fault. "
        "If and only if the brief passes all four checks, respond with exactly "
        "the single word APPROVED and nothing else.",
    )

    print("\n[Researcher] Searching the web...")
    research_result = await client.send_message(
        content=f"Research this topic thoroughly: {topic}",
        thread_id=researcher_thread.thread_id,
        llm_provider=MODEL_PROVIDER,
        model_name=MODEL_NAME,
        web_search="Auto",
        memory="Auto",
    )
    findings = get_reply(research_result)
    print(f"[Researcher] Findings gathered ({len(findings)} chars).\n")

    brief = None
    feedback = ""
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[Synthesizer] Writing brief (attempt {attempt})...")
        synth_prompt = f"Research notes:\n{findings}"
        if brief:
            synth_prompt += f"\n\nPrevious brief was rejected. Issues:\n{feedback}\n\nPlease revise."

        synth_result = await client.send_message(
            content=synth_prompt,
            thread_id=synthesizer_thread.thread_id,
            llm_provider=MODEL_PROVIDER,
            model_name=MODEL_NAME,
        )
        brief = get_reply(synth_result)
        print("[Synthesizer] Brief drafted.\n")

        print("[Critic] Reviewing brief against sources...")
        critic_result = await client.send_message(
            content=f"Original research:\n{findings}\n\nBrief to review:\n{brief}",
            thread_id=critic_thread.thread_id,
            llm_provider=MODEL_PROVIDER,
            model_name=MODEL_NAME,
        )
        feedback = get_reply(critic_result)

        if feedback.strip().upper().startswith("APPROVED"):
            print("[Critic] Approved.\n")
            break
        else:
            print(f"[Critic] Rejected. Feedback:\n{feedback}\n")
    else:
        print("[Critic] Max retries reached, using last draft anyway.\n")

    print("=" * 60)
    print("FINAL BRIEF")
    print("=" * 60)
    print(brief)

    # Save to a markdown file for submission/demo purposes
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"brief_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Brief: {topic}\n\n")
        f.write(brief)
    print(f"\n✅ Saved to {filename}")


if __name__ == "__main__":
    asyncio.run(main())