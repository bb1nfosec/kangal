from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os
from datetime import datetime
import re

os.makedirs('./crew_memory', exist_ok=True)
os.makedirs('./osint_results', exist_ok=True)

os.environ['SERPER_API_KEY'] = '**'  # Replace with your serper.dev API key
os.environ['OTEL_SDK_DISABLED'] = 'true'  # Disable telemetry
os.environ['CREWAI_STORAGE_DIR'] = os.path.abspath('./crew_memory')  # Storage for memory

# Initialize tools from crewai[tools]
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

search_tool = SerperDevTool(
    n_results=10,
    country="ru",
    locale="ru"
)
scrape_tool = ScrapeWebsiteTool()

# Create main agents
lead_analyst = Agent(
    role='Lead OSINT Analyst',
    goal='Coordinate OSINT research and analyze collected data',
    backstory="""An experienced analyst with deep OSINT knowledge. 
    Specializes in building comprehensive profiles based on digital footprints.
    Skilled in effective task delegation and integrating various information sources.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=True
)

social_expert = Agent(
    role='Social Media Expert',
    goal='Find and analyze social media profiles',
    backstory="""A specialist in social media analysis and online behavior.
    Skilled in finding related accounts and identifying activity patterns.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

technical_analyst = Agent(
    role='Technical Analyst',
    goal='Analyze technical information and digital footprints',
    backstory="""An expert in technical intelligence.
    Specializes in analyzing domains, IPs, data leaks, and technical metadata.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

behavior_analyst = Agent(
    role='Behavioral Analyst',
    goal='Analyze behavioral patterns and connections',
    backstory="""A specialist in behavioral analysis.
    Skilled in identifying interests, connections, and behavior patterns based on digital footprints.""",
    tools=[search_tool],
    verbose=True
)

verification_expert = Agent(
    role='Data Verification Expert',
    goal='Verify the reliability of collected information',
    backstory="""A specialist in verifying and confirming OSINT data.
    Uses cross-reference analysis and multiple sources for verification.
    Skilled in identifying misinformation and false leads.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

deep_search_expert = Agent(
    role='Deep Search Expert',
    goal='Find hidden and hard-to-access information',
    backstory="""A specialist in deep OSINT search.
    Skilled in finding information in archives, historical data, and specialized databases.
    Specializes in uncovering non-obvious connections and hidden data.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

task_keeper = Agent(
    role='Task Keeper',
    goal='Ensure the research stays focused on the assigned task',
    backstory="""A specialist in managing research focus.
    Tracks the alignment of all actions with the initial task.
    Helps agents stay on track with the research goal.""",
    tools=[search_tool],
    verbose=True
)

context_analyst = Agent(
    role='Context Analyst',
    goal='Maintain contextual integrity of the investigation',
    backstory="""An expert in contextual analysis.
    Combines disparate data into a unified context.
    Tracks the relevance of information relative to the task.""",
    tools=[search_tool],
    verbose=True
)

manager_agent = Agent(
    role='OSINT Manager',
    goal='Manage the investigation process and coordinate agent work',
    backstory="""An experienced OSINT investigation leader.
    Specializes in coordinating complex investigations and managing a team of analysts.
    Ensures effective agent interaction and result quality.""",
    tools=[],
    verbose=True,
    allow_delegation=True
)

def create_investigation_plan(target: str) -> List[Task]:
    """Create an investigation plan"""
    tasks = []
    
    tasks.append(Task(
        description=f"""
        Conduct a preliminary analysis of the target: {target}
        1. Identify main presence platforms
        2. Find key identifiers (email, username, etc.)
        3. Create an initial profile
        4. Determine priority areas for deep analysis
        
        Delegate subtasks to other agents if necessary.
        """,
        expected_output="""Provide a structured report containing:
        1. List of found platforms
        2. Found identifiers
        3. Brief target profile
        4. Priority areas for further analysis""",
        agent=lead_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        Based on the preliminary analysis, investigate the social networks of {target}:
        1. Find all related profiles
        2. Analyze contacts and connections
        3. Study activity history
        4. Identify behavioral patterns
        """,
        expected_output="""Provide a report including:
        1. List of found profiles with links
        2. Main contacts and connections
        3. Key points from activity history
        4. Identified behavioral patterns""",
        agent=social_expert
    ))
    
    tasks.append(Task(
        description=f"""
        Conduct a technical analysis of the found data on {target}:
        1. Check for data leaks
        2. Find related domains and IPs
        3. Analyze technical metadata
        4. Investigate digital footprints
        """,
        expected_output="""Provide a technical report containing:
        1. Found data leaks
        2. List of related technical identifiers
        3. Metadata analysis
        4. Digital footprint map""",
        agent=technical_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        Based on the collected data, analyze the behavior of {target}:
        1. Determine main interests
        2. Identify behavioral patterns
        3. Analyze social connections
        4. Create a psychological profile
        """,
        expected_output="""Provide a behavioral analysis including:
        1. Interest map
        2. Description of behavioral patterns
        3. Social connection diagram
        4. Psychological profile""",
        agent=behavior_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        Analyze all collected data on {target}:
        1. Combine information from all agents
        2. Identify data gaps
        3. Plan additional search directions
        4. Create a detailed target profile
        """,
        expected_output="""Provide a final report containing:
        1. Complete target profile
        2. Identified data gaps
        3. Plan for further investigation
        4. Main conclusions and recommendations""",
        agent=lead_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        Conduct a deep search for information on {target}:
        1. Investigate archival data and historical records
        2. Analyze specialized databases
        3. Find non-obvious connections and mentions
        4. Investigate rare and specific sources
        """,
        expected_output="""Provide a detailed report including:
        1. Found archival data
        2. Results from specialized database searches
        3. Identified non-obvious connections
        4. Information from rare sources""",
        agent=deep_search_expert
    ))
    
    tasks.append(Task(
        description=f"""
        Verify the reliability of all collected information on {target}:
        1. Conduct cross-reference analysis of data
        2. Confirm information from multiple sources
        3. Identify possible misinformation
        4. Assess the reliability of each source
        """,
        expected_output="""Provide a verification report including:
        1. Confirmed data with sources
        2. Debunked information
        3. Data requiring additional verification
        4. Source reliability assessment""",
        agent=verification_expert
    ))
    
    return tasks

def run_osint_investigation(target: str):
    """Run an OSINT investigation"""
    try:
        investigation_id = f"osint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        crew = Crew(
            agents=[
                lead_analyst,
                social_expert,
                technical_analyst,
                behavior_analyst,
                verification_expert,
                deep_search_expert,
                task_keeper,
                context_analyst
            ],
            tasks=create_investigation_plan(target),
            verbose=True,
            process=Process.hierarchical,
            manager_agent=manager_agent,
            memory=False,  
            planning=True
        )
        
        result = crew.kickoff()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs('osint_results', exist_ok=True)
        
        with open(f'osint_results/investigation_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(f"OSINT Investigation Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Assigned task: {target}\n")
            f.write("=" * 50 + "\n\n")
            f.write(str(result))
        
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def parse_osint_query(query: str) -> str:
    """Convert a query in the format "Enter target for OSINT: ..." into a task for agents"""
    if "Enter target for OSINT:" in query:
        query = query.replace("Enter target for OSINT:", "").strip()
    
    task_description = f"""
    Investigation target: {query}
    
    Required:
    1. Find all available information on the target
    2. Verify provided assumptions about age
    3. If requested - determine the birth month
    4. If requested - check presence on specialized forums
    
    Original query: {query}
    """
    
    return task_description

if __name__ == "__main__":
    query = input("Enter target for OSINT: ")
    formatted_task = parse_osint_query(query)
    result = run_osint_investigation(formatted_task)
    if result:
        print("\nInvestigation results:")
        print(result)