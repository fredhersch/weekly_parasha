# agents/script_agent.py
from agno.agent import Agent
from agno.models.anthropic import Claude

script_agent = Agent(
    name="Podcast Script Agent", 
    role="Transform Torah insights into an engaging podcast script",
    model=Claude(id="claude-sonnet-4-6"),
    tools=[],
    instructions=[
        "Write a 6-8 minute podcast script (approximately 750-1250 words)",
        "Structure: Hook (30s) → Parsha intro (1min) → Deep dive (4min) → Life application (2min) → Close (1min)",
        "Use conversational language — write for the ear, not the eye",
        "Include natural transitions and rhetorical questions to engage the listener",
        "Start with a compelling story or question that draws people in",
        "End with a practical takeaway the listener can apply this week",
        "Format with [PAUSE], [EMPHASIS], [MUSIC CUE] stage directions"
    ],
    markdown=True,
)