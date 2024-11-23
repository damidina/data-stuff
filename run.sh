#!/bin/bash

# Create project structure
mkdir -p project/{agents,utils,templates,config}

# Create .env file
cat > project/.env << 'EOL'
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_VERSION=2023-06-01
MODEL_NAME=claude-3-sonnet-20240229

# Agent System Prompts
DATA_SPECIALIST_PROMPT="You are a Data Specialist AI agent. Your role is to analyze data patterns, identify correlations, and communicate findings clearly. You should focus on statistical analysis and data interpretation."

REPORT_GENERATOR_PROMPT="You are a Report Generator AI agent. Your role is to receive analysis from the Data Specialist and create clear, well-structured reports. You should focus on presenting information in an accessible and actionable format."
EOL

# Create requirements.txt
cat > project/requirements.txt << 'EOL'
anthropic
python-dotenv
pandas
numpy
scipy
flask
EOL

# Create config.py
cat > project/config/config.py << 'EOL'
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_VERSION = os.getenv('ANTHROPIC_VERSION')
MODEL_NAME = os.getenv('MODEL_NAME')

# Agent System Prompts
DATA_SPECIALIST_PROMPT = os.getenv('DATA_SPECIALIST_PROMPT')
REPORT_GENERATOR_PROMPT = os.getenv('REPORT_GENERATOR_PROMPT')
EOL

# Create main.py
cat > project/main.py << 'EOL'
from flask import Flask, render_template, request, jsonify
from agents.data_specialist import DataSpecialist
from agents.report_generator import ReportGenerator
from utils.message_bus import MessageBus

app = Flask(__name__)
message_bus = MessageBus()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    # Initialize agents
    data_specialist = DataSpecialist(message_bus)
    report_generator = ReportGenerator(message_bus)
    
    # Process data
    analysis_result = data_specialist.analyze_data(data)
    final_report = report_generator.get_final_report()
    
    return jsonify({
        'analysis': analysis_result,
        'report': final_report
    })

if __name__ == '__main__':
    app.run(debug=True)
EOL

# Create data_specialist.py
cat > project/agents/data_specialist.py << 'EOL'
from anthropic import Anthropic
from config.config import ANTHROPIC_API_KEY, MODEL_NAME, DATA_SPECIALIST_PROMPT

class DataSpecialist:
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
    def analyze_data(self, data):
        try:
            # Prepare the prompt for Claude
            prompt = f"""
            {DATA_SPECIALIST_PROMPT}
            
            Please analyze the following data and identify patterns:
            {data}
            
            Focus on:
            1. Correlation between feedback and sales
            2. Regional patterns
            3. Key insights
            """
            
            # Call Claude API
            message = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            analysis = message.content[0].text
            
            # Send analysis to message bus
            self.message_bus.send_message({
                "type": "analysis_results",
                "content": analysis
            })
            
            return analysis
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.message_bus.send_message({
                "type": "error",
                "message": error_msg
            })
            return error_msg
EOL

# Create report_generator.py
cat > project/agents/report_generator.py << 'EOL'
from anthropic import Anthropic
from config.config import ANTHROPIC_API_KEY, MODEL_NAME, REPORT_GENERATOR_PROMPT

class ReportGenerator:
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.analysis_results = None
        self.message_bus.subscribe(self._handle_message)
        
    def _handle_message(self, message):
        if message["type"] == "analysis_results":
            self.analysis_results = message["content"]
        elif message["type"] == "error":
            print(f"Error received: {message['message']}")
    
    def get_final_report(self):
        if not self.analysis_results:
            return "No analysis results available."
        
        prompt = f"""
        {REPORT_GENERATOR_PROMPT}
        
        Please create a clear and structured report based on this analysis:
        {self.analysis_results}
        
        Format the report with clear sections and bullet points.
        """
        
        message = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
EOL

# Create message_bus.py
cat > project/utils/message_bus.py << 'EOL'
class MessageBus:
    def __init__(self):
        self.subscribers = []
        self.messages = []
    
    def subscribe(self, callback):
        self.subscribers.append(callback)
    
    def send_message(self, message):
        self.messages.append(message)
        for subscriber in self.subscribers:
            subscriber(message)
    
    def get_messages(self):
        return self.messages
EOL

# Create HTML template
cat > project/templates/index.html << 'EOL'
<!DOCTYPE html>
<html>
<head>
    <title>AI Agents Analysis</title>
    <style>
        body { max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; }
        .container { margin-top: 20px; }
        textarea { width: 100%; height: 200px; margin-bottom: 20px; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
        #result { margin-top: 20px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>AI Agents Analysis</h1>
    <div class="container">
        <textarea id="data" placeholder="Enter your data in JSON format..."></textarea>
        <button onclick="analyzeData()">Analyze</button>
        <div id="result"></div>
    </div>

    <script>
        async function analyzeData() {
            const data = document.getElementById('data').value;
            const result = document.getElementById('result');
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: data
                });
                
                const jsonResponse = await response.json();
                result.innerHTML = `
                    <h2>Analysis Results:</h2>
                    <pre>${jsonResponse.analysis}</pre>
                    <h2>Final Report:</h2>
                    <pre>${jsonResponse.report}</pre>
                `;
            } catch (error) {
                result.innerHTML = `Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
EOL

# Create __init__.py files
touch project/agents/__init__.py
touch project/utils/__init__.py
touch project/config/__init__.py

# Create virtual environment
python3 -m venv project/venv

# Activate virtual environment
source project/venv/bin/activate

# Install requirements
pip install -r project/requirements.txt

# Instructions for running
echo "
Setup complete! To run the application:

1. Edit project/.env and add your Anthropic API key
2. Activate the virtual environment:
   source project/venv/bin/activate
3. Run the Flask application:
   cd project && python main.py
4. Open http://localhost:5000 in your browser

The application will now be running with two AI agents:
- Data Specialist: Analyzes patterns in your data
- Report Generator: Creates structured reports from the analysis

Sample data format:
{
    \"sales\": [120, 150, 80, 200, 90],
    \"customer_feedback\": [\"great\", \"poor\", \"great\", \"medium\", \"poor\"],
    \"region\": [\"north\", \"south\", \"north\", \"east\", \"west\"]
}
"

# Deactivate virtual environment
deactivate