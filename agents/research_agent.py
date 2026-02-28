# agents/research_agent.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from tools.sepharia_tools import get_parsha_info

research_agent = Agent(
    name="Torah Research Agent",
    role="Fetch and analyze the weekly Torah portion and its major commentaries",
    model=Claude(id="claude-sonnet-4-6"),
    tools=[get_parsha_info],
    instructions=[
        "Always start by calling get_parsha_info to get the current parsha",
        "Draw on your knowledge of the text, Rashi, Ramban, and Midrash",
        "Identify 2-3 key themes or questions the parsha raises",
        "Return a structured research summary with: parsha name, key verses, themes, and commentary highlights"
    ],
    markdown=True,
)