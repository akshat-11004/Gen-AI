from crewai import LLM, Agent
from tools import yt_tool

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = LLM(
    model="gpt-5.6-luna",
    max_completion_tokens=4000,
    reasoning_effort="low"
    )

## Create a senior blog content researcher

blog_researcher=Agent(
    role='Blog Researcher from Youtube Videos',
    goal='get the relevant video transcription for the topic {topic} from the provided Yt channel',
    verboe=True,
    memory=True,
    backstory=(
       "Expert blog researcher with a keen eye for detail and a passion for uncovering the latest trends in technology." 
    ),
    llm=llm,
    tools=[yt_tool],
    allow_delegation=True
)

## creating a senior blog writer agent with YT tool

blog_writer=Agent(
    role='Blog Writer',
    goal='Narrate compelling tech stories about the video {topic} from YT video',
    verbose=True,
    memory=True,
    backstory=(
        "Expert blog writer with a talent for transforming complex technical concepts into engaging narratives summary within set token limit)."
    ),
    llm=llm,
    tools=[yt_tool],
    allow_delegation=False
)