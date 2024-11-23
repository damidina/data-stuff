from utils.message_bus import MessageBus
from anthropic import Anthropic
import json
import os
from datetime import datetime
from config.agent_config import AgentConfig

class ReportGenerator:
    def __init__(self, message_bus: MessageBus, config: AgentConfig):
        self.message_bus = message_bus
        self.config = config
        self.anthropic = Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.system_prompt = config.system_prompt
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.name = config.name
        self.description = config.description

    def generate_report(self, analysis: dict) -> dict:
        try:
            initial_analysis = analysis.get('content', '')

            # Ask for clarification with correct API format
            clarification_response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Based on this analysis, what clarifications are needed?\n\n{initial_analysis}"
                    }
                ]
            )

            clarification_request = clarification_response.content[0].text

            # Send clarification request through message bus
            self.message_bus.send_message(
                sender=self.name,
                receiver="Data Specialist",
                content=clarification_request
            )

            # Generate final report with correct API format
            final_report_response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": initial_analysis
                    },
                    {
                        "role": "assistant",
                        "content": clarification_request
                    },
                    {
                        "role": "user",
                        "content": "Generate a final report summarizing all findings"
                    }
                ]
            )

            final_report = final_report_response.content[0].text

            return {
                "conversation": [
                    {
                        "role": "Data Specialist",
                        "content": initial_analysis,
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "role": self.name,
                        "content": clarification_request,
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {
                            "description": self.description
                        }
                    },
                    {
                        "role": self.name,
                        "content": final_report,
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {
                            "description": self.description
                        }
                    }
                ],
                "final_report": final_report
            }

        except Exception as e:
            print(f"Error in generate_report: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }