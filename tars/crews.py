from crewai import Agent, Task, Crew, Process
import time
import json
import sys
import os
import routers
import tasks
import dynamic_tasks
import agents
import support
import config

def networkPentTester(question):
    return Crew(
        agents=[
            agents.NetworkPentester,
            agents.ResearcherAgent,
            agents.WriterAgent,
            agents.MakeMarkDownAgent,
        ],
        tasks=[
            dynamic_tasks.pentest_task(question, agents.NetworkPentester),
            tasks.cybersecurity_research,
            tasks.build_cybersecurity_report,
            tasks.convert_report_to_markdown,
        ],
        process=Process.sequential,
        memory=True,
        cache=True,
        full_output=True,
    )

def WebAppPentTester(question):
    return Crew(
        agents=[
            agents.WebAppPentester,
            agents.ResearcherAgent,
            agents.WriterAgent,
            agents.MakeMarkDownAgent,
        ],
        tasks=[
            dynamic_tasks.webapp_pentest_task(question, agents.WebAppPentester),
            tasks.cybersecurity_research,
            tasks.build_cybersecurity_report,
            tasks.convert_report_to_markdown,
        ],
        process=Process.sequential,
        memory=True,
        cache=True,
        full_output=True,
    )

# NOTE: this is just for testing, DO NOT use in production!
def testCrew():
    return Crew(
        agents=[agents.WriterAgent],
        tasks=[tasks.build_cybersecurity_report],
        process=Process.sequential,
        memory=True,
        cache=True,
        full_output=True,
    )

# MAIN CREW ALL WITH LOGIC IF STATEMENTS
def call_crew(user_question):
    try:
        # Get routing classification
        prompt_router = routers.prompt_route(
            config.router_model_name,
            config.router_config,
            user_question,
        )
        
        # Debug: Print the routing result
        print(f"DEBUG: Raw router response: '{prompt_router}'")
        
        # Handle the response - split by comma and clean up
        if prompt_router:
            prompt_router_list = [item.strip() for item in prompt_router.split(",")]
            print(f"DEBUG: Parsed categories: {prompt_router_list}")
        else:
            prompt_router_list = []
        
        question = user_question
        crew = None
        
        # More flexible matching logic
        for category in prompt_router_list:
            if "Web Application" in category or "web" in category.lower():
                print("Using Web-App Pentesting crew")
                crew = WebAppPentTester(question)
                break
            elif "Network" in category or "network" in category.lower():
                print("Using Network Pentesting crew")
                crew = networkPentTester(question)
                break
        
        # Fallback logic based on keywords in the question
        if crew is None:
            question_lower = user_question.lower()
            print(f"DEBUG: No direct category match. Analyzing question keywords...")
            
            # Web application keywords
            web_keywords = ["web", "website", "html", "javascript", "sql injection", "xss", "csrf", "web app", "http", "https"]
            # Network keywords  
            network_keywords = ["network", "port", "scan", "ping", "firewall", "router", "switch", "tcp", "udp", "ip"]
            
            web_score = sum(1 for keyword in web_keywords if keyword in question_lower)
            network_score = sum(1 for keyword in network_keywords if keyword in question_lower)
            
            print(f"DEBUG: Web score: {web_score}, Network score: {network_score}")
            
            if web_score > network_score and web_score > 0:
                print("Using Web-App Pentesting crew (keyword fallback)")
                crew = WebAppPentTester(question)
            elif network_score > 0:
                print("Using Network Pentesting crew (keyword fallback)")
                crew = networkPentTester(question)
        
        # Final fallback - default to network pentesting
        if crew is None:
            print("DEBUG: No category matched. Defaulting to Network Pentesting crew")
            crew = networkPentTester(question)
        
        # # TODO: remove after testing
        # crew = testCrew()
        
        start_time = time.time()
        
        try:
            result = crew.kickoff()
            runtime = time.time() - start_time
            return {
                "result": support.crewai_result_to_json(result),
                "runtime": {"runtime": runtime, "unit": "seconds"},
            }
        except Exception as e:
            runtime = time.time() - start_time
            return {
                "error": str(e),
                "runtime": {"runtime": runtime, "unit": "seconds"},
            }
            
    except Exception as routing_error:
        print(f"ERROR in routing: {routing_error}")
        # Emergency fallback
        print("Using emergency fallback to Network Pentesting crew")
        crew = networkPentTester(user_question)
        
        start_time = time.time()
        try:
            result = crew.kickoff()
            runtime = time.time() - start_time
            return {
                "result": support.crewai_result_to_json(result),
                "runtime": {"runtime": runtime, "unit": "seconds"},
            }
        except Exception as e:
            runtime = time.time() - start_time
            return {
                "error": str(e),
                "runtime": {"runtime": runtime, "unit": "seconds"},
            }