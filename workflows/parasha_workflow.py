# workflows/parasha_workflow.py
from agno.workflow import Workflow, Step, StepInput, StepOutput
from agents.research_agent import research_agent
from agents.commentary_agent import commentary_agent
from agents.script_agent import script_agent
from agents.daily_agents import daily_reflection_agent, dvar_torah_agent

def research_step(step_input: StepInput) -> StepOutput:
    theme = step_input.input or ""
    prompt = "Research this week's Torah portion. Use get_parsha_info to get the current parasha, then draw on your knowledge of the text, Rashi, Ramban, and key themes."
    if theme and theme != "general themes":
        prompt += f" Focus especially on the theme of: {theme}"
    result = research_agent.run(prompt)
    return StepOutput(content=result.content)

def commentary_step(step_input: StepInput) -> StepOutput:
    prior = step_input.previous_step_content or ""
    result = commentary_agent.run(
        f"Based on this research, generate deep insights:\n\n{prior}"
    )
    return StepOutput(content=result.content)

def script_step(step_input: StepInput) -> StepOutput:
    prior = step_input.previous_step_content or ""
    result = script_agent.run(
        f"Create a podcast script from this commentary:\n\n{prior}"
    )
    return StepOutput(content=result.content)

def daily_reflection_step(step_input: StepInput) -> StepOutput:
    prior = step_input.previous_step_content or ""
    result = daily_reflection_agent.run(
        f"Based on this research and commentary, create 5 daily parasha reflections:\n\n{prior}"
    )
    return StepOutput(content=result.content)

def dvar_torah_step(step_input: StepInput) -> StepOutput:
    prior = step_input.previous_step_content or ""
    result = dvar_torah_agent.run(
        f"Based on this research and commentary, write a Dvar Torah for the Shabbat table:\n\n{prior}"
    )
    return StepOutput(content=result.content)

# Full weekly workflow — research + commentary + podcast
torah_workflow = Workflow(
    name="Torah Study Workflow",
    steps=[
        Step(name="research", executor=research_step),
        Step(name="commentary", executor=commentary_step),
        Step(name="script", executor=script_step),
    ]
)

# Daily + Dvar Torah workflow — research + commentary + dailies + dvar
torah_daily_workflow = Workflow(
    name="Torah Daily Workflow",
    steps=[
        Step(name="research", executor=research_step),
        Step(name="commentary", executor=commentary_step),
        Step(name="dailies", executor=daily_reflection_step),
        Step(name="dvar_torah", executor=dvar_torah_step),
    ]
)