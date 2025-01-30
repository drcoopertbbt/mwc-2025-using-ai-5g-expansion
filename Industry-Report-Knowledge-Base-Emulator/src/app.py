from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
import json
import os
import markdown
from datetime import datetime
import re
from openai import OpenAI
from dotenv import load_dotenv
import logging
import traceback
import sys
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Ensure all loggers are set to DEBUG
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('openai').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Force immediate flush of logging
sys.stdout.flush()
sys.stderr.flush()

print("=== Industry Report Knowledge Base Starting ===")
print("Logging Level: DEBUG")
print("Console Output: Enabled")
print("================================")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")
print("API Key loaded from .env file")

def load_industry_data():
    data_path = os.path.join(os.path.dirname(__file__), 'data/industry-data/industry_data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

class APILogger:
    @staticmethod
    def log_auth_attempt(api_key):
        logger.info("=== NVIDIA API Authentication ===")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"API Key Format: nvapi-{api_key[:4]}...{api_key[-4:]}")
        logger.info("Auth Method: Bearer Token")
        logger.info("Auth Scope: chat.completions")
        logger.info("==============================")

    @staticmethod
    def log_request_start(api_key, url):
        logger.info("=== NVIDIA API Request Start ===")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Request ID: {datetime.now().strftime('%Y%m%d%H%M%S')}")
        logger.info(f"Endpoint: {url}")
        logger.info("=== Request Headers ===")
        logger.info("Content-Type: application/json")
        logger.info("Authorization: Bearer nvapi-***")
        logger.info("Accept: application/json")
        logger.info("User-Agent: MWC-Industry-Report-KB/1.0")
        logger.info("Connection: keep-alive")
        logger.info("========================")

    @staticmethod
    def log_request_end(response_status, duration=None):
        logger.info("=== NVIDIA API Response ===")
        logger.info(f"Status: {response_status}")
        if duration:
            logger.info(f"Response Time: {duration:.2f}s")
        logger.info("=== Response Headers ===")
        logger.info("Content-Type: application/json")
        logger.info("X-Request-ID: Present")
        logger.info("X-RateLimit-Limit: Standard")
        logger.info("X-RateLimit-Remaining: Tracked")
        logger.info("=========================")

def generate_ai_response(prompt, context):
    try:
        print("\n=== NVIDIA API Chat Request ===")
        
        api_key = os.getenv('NVIDIA_API_KEY')
        if not api_key:
            raise Exception("NVIDIA_API_KEY environment variable is not set")
        base_url = "https://integrate.api.nvidia.com/v1"
        
        system_message = """You are an Industry Report Analysis AI assistant specializing in 5G and healthcare technology trends. 
        When responding to queries:
        1. Analyze industry reports to identify key trends, market valuations, and growth projections
        2. Focus on technological convergence between 5G, AI, and healthcare applications
        3. Highlight implementation challenges, risk factors, and mitigation strategies
        4. Evaluate market opportunities and strategic considerations
        5. Provide data-driven insights using specific metrics from the reports
        
        Structure your responses to include:
        - Market Overview: Current state and projections
        - Key Technologies: Focus areas and innovations
        - Implementation Analysis: Challenges and solutions
        - Strategic Insights: Opportunities and recommendations
        
        Conclude with a summary highlighting:
        - Critical market metrics and growth indicators
        - Key technological trends and their impact
        - Primary challenges and mitigation strategies
        - Strategic recommendations for stakeholders
        
        Format responses using Markdown for clarity:
        - Use headers (##) for main sections
        - Bullet points for lists
        - **Bold** for important metrics/figures
        - `Code blocks` for technical specifications
        - > Blockquotes for direct insights from reports"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "meta/llama-3.3-70b-instruct",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Context:\n{context}\n\nQuery: {prompt}"}
            ],
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 1024,
            "stream": True
        }
        
        print(f"\nTimestamp: {datetime.now().isoformat()}")
        print("\nRequest Configuration:")
        print("- Model: meta/llama-3.3-70b-instruct")
        print("- Temperature: 0.2")
        print("- Top_p: 0.7")
        print("- Max tokens: 1024")
        print("- Stream: enabled")
        print("\nMessage Details:")
        print(f"- System message: {len(system_message)} chars")
        print(f"- Context: {len(context)} chars")
        print(f"- User query: {len(prompt)} chars")
        print("\nAPI Endpoint: /chat/completions")
        print("Request Method: POST")
        sys.stdout.flush()
        
        print("\nSending request to NVIDIA API...")
        sys.stdout.flush()
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            stream=True
        )
        
        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        print("Request accepted by API")
        print("Initializing streaming response...")
        print("Content-Type: text/event-stream")
        print("Transfer-Encoding: chunked")
        print("================================")
        sys.stdout.flush()
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        logger.error(traceback.format_exc())
        raise

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Create local data directories for testing
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')
os.makedirs(os.path.join(data_dir, 'prompts'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'responses'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'rag-database'), exist_ok=True)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        print("\n=== New Request Received ===")
        logger.info("Received /ask request")
        sys.stdout.flush()
        
        # Extract prompt from the incoming request
        prompt_data = request.json.get('prompt', '')
        logger.info(f"Processing prompt: {prompt_data}")
        print(f"User Query: {prompt_data}")
        sys.stdout.flush()
        
        # Save the prompt
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        prompt_path = os.path.join(data_dir, 'prompts', f'prompt_{timestamp}.json')
        with open(prompt_path, 'w') as f:
            json.dump({'prompt': prompt_data}, f, indent=2)

        # Load and structure industry data as context
        industry_data = load_industry_data()
        
        # Format the context in a more structured way
        context = "Here is our industry report data:\n\n"
        for report in industry_data['industry_reports']:
            context += f"Report: {report['title']}\n"
            context += f"ID: {report['report_id']}\n"
            context += f"Sector: {report['sector']}\n"
            context += f"Date: {report['date']}\n\n"
            
            context += "Key Findings:\n"
            for finding in report['key_findings']:
                context += f"- Category: {finding['category']}\n"
                if 'data' in finding:
                    for key, value in finding['data'].items():
                        if isinstance(value, list):
                            context += f"  {key}:\n"
                            for item in value:
                                context += f"    - {item}\n"
                        else:
                            context += f"  {key}: {value}\n"
                context += f"  Analysis: {finding['analysis']}\n\n"
            
            context += "Trends:\n"
            for trend in report['trends']:
                context += f"- {trend['name']} (Impact: {trend['impact']})\n"
                context += f"  {trend['description']}\n"
            
            context += f"\nSource: {report['source']['url']}\n"
            context += f"Published: {report['source']['published_date']}\n"
            context += f"Tags: {', '.join(report['tags'])}\n\n"
            context += "---\n\n"
            
        logger.info("Context prepared, initiating response generation")

        def generate():
            try:
                print("\n=== Starting API Interaction ===")
                sys.stdout.flush()
                
                response = generate_ai_response(prompt_data, context)
                collected_messages = []
                buffer = []
                
                chunk_count = 0
                total_chars = 0
                print("Streaming response from NVIDIA API...")
                sys.stdout.flush()
                start_time = datetime.now()

                # Configure markdown with all necessary extensions
                md = markdown.Markdown(
                    extensions=[
                        'markdown.extensions.extra',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.tables',
                        'markdown.extensions.toc'
                    ],
                    extension_configs={
                        'markdown.extensions.codehilite': {
                            'css_class': 'highlight',
                            'use_pygments': True,
                            'noclasses': False
                        }
                    }
                )
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                content = json.loads(line[6:])
                                if content.get('choices') and content['choices'][0].get('delta', {}).get('content'):
                                    message = content['choices'][0]['delta']['content']
                                    chunk_count += 1
                                    total_chars += len(message)
                                    collected_messages.append(message)
                                    buffer.append(message)
                                    
                                    # Join the buffer to check for complete markdown blocks
                                    current_text = ''.join(buffer)
                                    
                                    # Check for complete markdown blocks
                                    if (
                                        '\n\n' in message or
                                        message.strip().endswith('```') or
                                        message.rstrip().endswith('.') or
                                        message.strip().endswith('---') or
                                        message.strip().endswith(')') or
                                        len(buffer) > 50  # Flush buffer if it gets too large
                                    ):
                                        # Convert accumulated text to HTML
                                        html_content = md.convert(current_text)
                                        buffer = []  # Clear buffer after conversion
                                        
                                        # Reset markdown instance for next conversion
                                        md.reset()
                                        
                                        yield f"data: {json.dumps({'content': html_content})}\n\n"
                                    
                                    if chunk_count % 10 == 0:  # Log every 10th chunk
                                        print(f"Received {chunk_count} chunks ({total_chars} chars)")
                                        sys.stdout.flush()
                            except json.JSONDecodeError:
                                continue
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info("=== Streaming Complete ===")
                logger.info(f"Total chunks: {chunk_count}")
                logger.info(f"Total characters: {total_chars}")
                logger.info(f"Duration: {duration:.2f} seconds")
                logger.info(f"Average speed: {total_chars/duration:.2f} chars/second")
                logger.info("========================")
                
                # Save the complete response
                full_response = ''.join(collected_messages)
                response_path = os.path.join(data_dir, 'responses', f'response_{timestamp}.json')
                with open(response_path, 'w') as f:
                    json.dump({'response': full_response}, f, indent=2)
                
                # Save to RAG database
                rag_entry = {
                    'query': prompt_data,
                    'response': full_response,
                    'timestamp': timestamp
                }
                rag_path = os.path.join(data_dir, 'rag-database', f'entry_{timestamp}.json')
                with open(rag_path, 'w') as f:
                    json.dump(rag_entry, f, indent=2)
                
            except Exception as e:
                logger.error(f"Error in generate(): {str(e)}")
                logger.error(traceback.format_exc())
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Error in /ask route: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
