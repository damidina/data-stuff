from utils.message_bus import MessageBus
import json
import pandas as pd
from anthropic import Anthropic
import os
from datetime import datetime

class DataSpecialist:
    def __init__(self, message_bus: MessageBus, config: dict):
        self.message_bus = message_bus
        self.config = config
        self.anthropic = Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.system_prompt = config['system_prompt']
        self.temperature = config['temperature']
        self.max_tokens = config['max_tokens']

    def analyze_data(self, data: str) -> dict:
        try:
            # Parse input data
            try:
                if isinstance(data, str):
                    if 'data = ' in data:
                        data = data.replace('data = ', '')
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                parsed_data = {"raw_input": data}

            # Get analysis from Claude
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze this data and identify key patterns and anomalies:\n{json.dumps(parsed_data, indent=2)}"}
                ]
            )

            analysis = response.content[0].text
            
            # Send the analysis to the message bus
            self.message_bus.send_message(
                sender="Data Specialist",
                receiver="Report Generator",
                content=analysis
            )

            return {
                "role": "Data Specialist",
                "content": analysis,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error in analyze_data: {str(e)}")
            return {
                "error": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed"
                }
            }