from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv
import os
from .prompts import DATA_SPECIALIST_PROMPT, REPORT_GENERATOR_PROMPT

# Load environment variables
load_dotenv()

@dataclass
class AgentConfig:
    name: str
    description: str
    system_prompt: str
    temperature: float
    max_tokens: int
    tools: Optional[List[dict]] = None

def get_agent_configs():
    return {
        "data_specialist": AgentConfig(
            name="Data Specialist",
            description="Analyzes patterns and correlations in data",
            system_prompt=DATA_SPECIALIST_PROMPT,
            temperature=0.3,
            max_tokens=1500,
            tools=[{
                "name": "analyze_correlation",
                "description": "Calculate correlation between variables",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "variable1": {"type": "array", "description": "First variable"},
                        "variable2": {"type": "array", "description": "Second variable"}
                    }
                }
            }]
        ),
        "report_generator": AgentConfig(
            name="Report Generator",
            description="Creates structured reports from analysis",
            system_prompt=REPORT_GENERATOR_PROMPT,
            temperature=0.7,
            max_tokens=2000
        )
    }