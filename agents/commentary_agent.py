# agents/commentary_agent.py
from agno.agent import Agent
from agno.models.anthropic import Claude

commentary_agent = Agent(
    name="Commentary Synthesis Agent",
    role="Synthesize multiple commentaries into original Torah insights",
    model=Claude(id="claude-sonnet-4-6"),
    tools=[],
    instructions=[
        "Take the research summary and deepen the commentary",
        "Compare how Rashi and Ramban approach key verses differently",
        "Find contemporary relevance — connect ancient wisdom to modern life",
        "Identify the central life lesson (mussar) of the parsha",
        "Keep insights accessible to a general audience, not just scholars",
        "Produce 3-4 original insights, each 2-3 paragraphs"
    ],
    markdown=True,
)