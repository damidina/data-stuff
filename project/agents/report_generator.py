from utils.message_bus import MessageBus
from anthropic import Anthropic
import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, message_bus: MessageBus, config: dict):
        self.message_bus = message_bus
        self.config = config
        self.anthropic = Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.system_prompt = config['system_prompt']
        self.temperature = config['temperature']
        self.max_tokens = config['max_tokens']

    def generate_report(self, analysis: dict) -> dict:
        try:
            # Get the analysis from the Data Specialist
            initial_analysis = analysis.get('content', '')

            # Ask for clarification if needed
            clarification_response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Based on this analysis, what clarifications are needed?\n\n{initial_analysis}"}
                ]
            )

            clarification_request = clarification_response.content[0].text

            # Send clarification request through message bus
            self.message_bus.send_message(
                sender="Report Generator",
                receiver="Data Specialist",
                content=clarification_request
            )

            # Generate final report
            final_report_response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": initial_analysis},
                    {"role": "assistant", "content": clarification_request},
                    {"role": "user", "content": "Generate a final report summarizing all findings"}
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
                        "role": "Report Generator",
                        "content": clarification_request,
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "role": "Report Generator",
                        "content": final_report,
                        "timestamp": datetime.now().isoformat()
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