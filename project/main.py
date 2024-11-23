from flask import Flask, render_template, request, jsonify
from agents.data_specialist import DataSpecialist
from agents.report_generator import ReportGenerator
from utils.message_bus import MessageBus
from config.agent_config import get_agent_configs
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import time
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

# Load environment variables
load_dotenv()

# Initialize Flask app and shared resources
app = Flask(__name__)
message_bus = MessageBus()
agent_configs = get_agent_configs()

class ConversationManager:
    def __init__(self):
        self.history = []
        self.error_count = 0
        self.start_time = None

    def start_conversation(self):
        self.start_time = time.time()
        self.history = []
        self.error_count = 0

    def add_message(self, role, content, metadata=None):
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.history.append(message)
        return message

    def get_conversation_stats(self):
        if not self.start_time:
            return {}
        return {
            'duration': time.time() - self.start_time,
            'message_count': len(self.history),
            'error_rate': self.error_count / len(self.history) if self.history else 0
        }

conversation_manager = ConversationManager()

@app.route('/')
def index():
    """Render the main page with conversation history"""
    stats = conversation_manager.get_conversation_stats()
    return render_template('index.html', 
                         conversation_history=conversation_manager.history,
                         stats=stats)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle the analysis request with retry mechanism and error handling"""
    data = request.json.get('input', '')
    retry_count = 0
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    if not data:
        return jsonify({'error': 'No input provided'}), 400
    
    logger.info(f"Processing request at {datetime.now()}")
    logger.info(f"Input data: {data[:100]}...")
    
    conversation_manager.start_conversation()
    
    while retry_count < MAX_RETRIES:
        try:
            # Initialize agents
            data_specialist = DataSpecialist(
                message_bus=message_bus,
                config=agent_configs["data_specialist"]
            )
            report_generator = ReportGenerator(
                message_bus=message_bus,
                config=agent_configs["report_generator"]
            )
            
            # Start analysis
            analysis_result = data_specialist.analyze_data(data)
            logger.info(f"Analysis completed at {datetime.now()}")
            
            if 'error' in analysis_result:
                raise Exception(analysis_result['error'])
            
            # Generate report
            report_result = report_generator.generate_report(analysis_result)
            logger.info(f"Report generated at {datetime.now()}")
            
            if 'error' in report_result:
                raise Exception(report_result['error'])
            
            # Add conversation to history
            conversation_manager.add_message('user', data)
            for message in report_result.get('conversation', []):
                conversation_manager.add_message(
                    message['role'],
                    message['content'],
                    message.get('metadata')
                )
            
            response = {
                'analysis': analysis_result,
                'report': report_result,
                'conversation': conversation_manager.history,
                'stats': conversation_manager.get_conversation_stats(),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'retry_count': retry_count
                }
            }
            
            return jsonify(response)
        
        except Exception as e:
            retry_count += 1
            conversation_manager.error_count += 1
            logger.error(f"Error in attempt {retry_count}: {str(e)}")
            logger.error(traceback.format_exc())
            
            if retry_count >= MAX_RETRIES:
                return jsonify({
                    'error': str(e),
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'status': 'error',
                        'retry_count': retry_count
                    }
                }), 500
            
            time.sleep(RETRY_DELAY)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed metrics"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'metrics': {
            'conversation_count': len(conversation_manager.history),
            'error_rate': conversation_manager.error_count / len(conversation_manager.history) if conversation_manager.history else 0,
            'uptime': time.time() - conversation_manager.start_time if conversation_manager.start_time else 0
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 4323))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )