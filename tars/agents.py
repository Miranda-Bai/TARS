from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from crewai_tools import (
    SerperDevTool,
    WebsiteSearchTool,
)

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI  # Fixed import
from subprocess import Popen, PIPE
import config
import sys
import os

sys.path.append(os.path.join(str("/".join(__file__.split("/")[:-1])), "tools"))
from tools import nettacker, helpers, scrapper, search, rustscan, zaproxy

# Configure OpenRouter LLM using ChatOpenAI (OpenAI-compatible)
openrouter_llm = ChatOpenAI(
    model=config.best_openrouter_model,  # e.g., "deepseek/deepseek-r1"
    openai_api_key=config.openrouter_api_key,  # Your OpenRouter API key
    openai_api_base=config.openrouter_api_base,  # OpenRouter API base
    temperature=0.7,
    max_tokens=2000,
    # Optional headers can be added via default_headers if needed
)

# NOTE: (5-3-2024) I did not give this agent access to a full scan tool(s)
WebAppPentester = Agent(
    role="Web Application Penetration Tester",
    goal="Perform comprehensive penetration tests on web applications to uncover and report vulnerabilities using advanced techniques and a variety of security tools.",
    backstory="""
As a seasoned web application penetration tester, you excel at simulating cyber attacks to pinpoint weaknesses in web applications. With extensive knowledge of web technologies and security practices, you have safeguarded numerous applications from potential threats. Your ability to think like a hacker and apply rigorous testing methodologies makes you a valuable asset in the cybersecurity field. You consistently update your skills to keep up with the latest vulnerabilities and defense mechanisms in web technologies.
""",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
    tools=[
        rustscan.rustscan,
        rustscan.rustscan_docs,
        zaproxy.zap_api_scan,
        zaproxy.zap_baseline_scan,
        zaproxy.zap_general_use,
    ],
)

NetworkPentester = Agent(
    role="Network Penetration Tester",
    goal="Execute advanced penetration tests to uncover and report network vulnerabilities using sophisticated techniques and tools.",
    backstory="""
As an expert network penetration tester, you specialize in simulating cyber attacks on networks to identify vulnerabilities before they can be exploited maliciously. With a deep understanding of security frameworks and tools, you have successfully fortified numerous enterprise networks against potential threats. Your analytical skills and strategic approach have earned you recognition in the cybersecurity community, and you continue to stay ahead of the curve by mastering emerging technologies and methodologies.
""",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
    tools=[
        nettacker.get_nettacker_docs,
        nettacker.nettacker,
        nettacker.nettacker_profile_all,
        nettacker.nettacker_module_all,
        rustscan.rustscan,
        rustscan.rustscan_docs,
        helpers.ping_ip,
    ],
)

ResearcherAgent = Agent(
    role="Cybersecurity Researcher",
    goal="Provide up-to-date solutions for specific cybersecurity issues/vulnerabilities",
    backstory="An expert analyst with a keen eye for cybersecurity and finding ways/sources to fix any cybersecurity issue/vulnerability",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
    tools=[
        scrapper.crawl_website_urls,
        scrapper.scrape_website,
        search.search_engine,
        WebsiteSearchTool(),
        SerperDevTool(),
    ],
)

WriterAgent = Agent(
    role="Report Writer",
    goal="Given some content/research, craft a nice, concise, informative, report detailing the findings in the research. The report must be in Markdown and, if need be, each source should be cited in a bibliography",
    backstory="A skilled Report Writer with a passion for writing the best Reports given the content/research presented to them",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
    tools=[helpers.current_utc_timestamp],
)

MakeMarkDownAgent = Agent(
    role="Markdown Converter",
    goal="Convert plain text into well-formatted Markdown, ensuring clean and professional documentation style.",
    backstory=(
        "As a Markdown conversion expert, you have a knack for transforming plain text into beautifully formatted Markdown. "
        "Your skill goes beyond mere conversion; you elevate plain text into an art form, creating Markdown that is not only "
        "functional but also aesthetically pleasing. You pride yourself on your ability to present complex information in an "
        "organized and engaging manner."
    ),
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
    tools=[],
)