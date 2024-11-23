import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_VERSION = os.getenv('ANTHROPIC_VERSION')
MODEL_NAME = os.getenv('MODEL_NAME')

# Agent System Prompts
DATA_SPECIALIST_PROMPT = os.getenv('DATA_SPECIALIST_PROMPT')
REPORT_GENERATOR_PROMPT = os.getenv('REPORT_GENERATOR_PROMPT')
