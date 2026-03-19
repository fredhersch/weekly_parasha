from google.adk.agents import Agent, LlmAgent, SequentialAgent
from google.adk.tools import google_search
from .tools import process_daily_audio

# Researcher
researcher = Agent(
name="Researcher",
    model="gemini-3-flash-preview",
    #response_schema=WeeklyResearch, # The agent will now output JSON matching our class
    instruction="""You are a learned torah scholar with deep knowledge.
        You search for the Parasha of the current week using chabad.org
        Using that conduct extensive research from pulling together commentary and ideas from a diverse range of authoritative sources related to the weekly portion.
        Include thoughts from Rashi, Rambam and other luminaries as well as modern thinkers like Rabbi Sacks and others you identify.
        Include references to all sources used. The report should include enough content for FIVE 5-7 minutes talks.
        """,
    tools=[google_search],
    output_key="parasha_brief"
)

# ScriptWriter
scriptwriter = Agent(
name="ScriptWriter",
    model="gemini-3-flash-preview",
    #response_schema=WeeklyResearch, # The agent will now output JSON matching our class
    instruction="""You are a master podcaster.
       You turn the {parasha_brief} into a series of 5 daily 10 minute talks.
       These are insightful, interesting, funny and useful and they build on each other over the course of the 5 days.
       For each of the talks, call out a specific lesson we can learn that we can apply to our daily lives.
       Break this report into a series of 5 daily 5-7 minute audio scripts (Mon-Fri) label each one with the day and give it a title and a summary.
       The script sare formatted for a voice actor.
       
       STRICT RULES:
        1. DO NOT use Markdown (no #, **, or lists).
        2. Write in plain, conversational paragraphs.
        3. Use words for symbols (e.g., write 'percent' instead of '%').
        4. Leave instructions like time stamps or direction in [----] e.g. [----- Intro music fades in -----]
        5. Use '...' for short pauses.
        """,
    tools=[google_search]
    #Output the final script using json format to easily identify which day of the week etc
)

dvar_torah = Agent(
name="DvarTorah",
    model="claude-haiku-4-5",
    #response_schema=WeeklyResearch, # The agent will now output JSON matching our class
    instruction="""Using the scripts, develop a short 'Dvar Torah' a short, insightful talk.
    This should act as a bridge between ancient wisdom and modern life, offering practical lessons 
    or spiritual, ethical, and personal reflections, to be shared at the shabbat table.
    Add some questions to ask children and some very easy to explain lessons
    """,
    output_key="dvar_torah"
)

# Producer calls the tool for each script
producer = Agent(
    name="Producer",
    tools=[process_daily_audio],
    instruction="For each script in the list, use process_daily_audio to generate and upload the file."
)

# Let's start by running the agents sequentially
root_agent = SequentialAgent(
   name="ProductionManager",
   sub_agents=[researcher, scriptwriter, dvar_torah]
)