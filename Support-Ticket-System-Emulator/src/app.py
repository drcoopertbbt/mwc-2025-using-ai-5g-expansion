from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import markdown
from datetime import datetime
import re

def load_knowledge_base():
    kb_path = os.path.join(os.path.dirname(__file__), 'data/knowledge_base/support_articles.json')
    with open(kb_path, 'r') as f:
        return json.load(f)

def search_knowledge_base(query, kb_data):
    query = query.lower()
    relevant_articles = []
    
    for article in kb_data['articles']:
        # Check title, content, and tags for matches
        if (query in article['title'].lower() or 
            query in article['content'].lower() or 
            query in ' '.join(article['tags']).lower() or
            query in article['category'].lower()):
            relevant_articles.append(article)
    
    return relevant_articles

app = Flask(__name__)
CORS(app)

# Create local data directories for testing
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')
os.makedirs(os.path.join(data_dir, 'prompts'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'responses'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'rag-database'), exist_ok=True)

@app.route('/ask', methods=['POST'])
def ask():
    # Extract prompt from the incoming request
    prompt_data = request.json.get('prompt', '')
    
    # Create a more focused customer support prompt
    enhanced_prompt = f"""As a customer support AI assistant, please help with the following query. 
    Use a professional and helpful tone. If you need more information, politely ask for it.
    
    Customer Query: {prompt_data}
    """

    # Save the prompt
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    prompt_path = os.path.join(data_dir, 'prompts', f'prompt_{timestamp}.json')
    with open(prompt_path, 'w') as f:
        json.dump({'prompt': prompt_data, 'enhanced_prompt': enhanced_prompt}, f, indent=2)

    # Load and search knowledge base
    kb_data = load_knowledge_base()
    relevant_articles = search_knowledge_base(prompt_data.lower(), kb_data)
    
    # Create context from relevant articles
    context = ""
    if relevant_articles:
        context = "Based on our knowledge base:\n\n"
        for article in relevant_articles:
            context += f"## {article['title']}\n{article['content']}\n\n"
    else:
        context = "No directly relevant articles found in our knowledge base. Providing a general response.\n\n"
    
    # Create response with knowledge base context
    response_body = {
        "choices": [{
            "message": {
                "content": f"Here's what I found to help with your query about '{prompt_data}':\n\n{context}\n\nIs there anything specific from this information you'd like me to clarify?"
            }
        }]
    }

    # Save the response
    response_path = os.path.join(data_dir, 'responses', f'response_{timestamp}.json')
    with open(response_path, 'w') as f:
        json.dump(response_body, f, indent=2)

    # Extract and format the response for RAG
    try:
        message_content = response_body['choices'][0]['message']['content']
        
        # Save to RAG database
        rag_entry = {
            'query': prompt_data,
            'response': message_content,
            'timestamp': timestamp
        }
        rag_path = os.path.join(data_dir, 'rag-database', f'entry_{timestamp}.json')
        with open(rag_path, 'w') as f:
            json.dump(rag_entry, f, indent=2)

        # Convert to HTML for display
        html_content = markdown.markdown(message_content)
        
        return jsonify({
            'response': message_content,
            'html': html_content,
            'timestamp': timestamp
        })

    except KeyError:
        return jsonify({
            'error': 'Invalid response format',
            'raw_response': response_body
        }), 500

@app.route('/')
def home():
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Support AI Assistant</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .chat-container { max-width: 800px; margin: auto; }
            .response { white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="container mt-5 chat-container">
            <h1 class="mb-4">Customer Support AI Assistant</h1>
            <div class="mb-3">
                <textarea id="prompt" class="form-control" rows="4" placeholder="Enter your support query here..."></textarea>
            </div>
            <button onclick="submitQuery()" class="btn btn-primary mb-4">Submit Query</button>
            <div id="response" class="response border rounded p-3 bg-light"></div>
        </div>

        <script>
        async function submitQuery() {
            const prompt = document.getElementById('prompt').value;
            const responseDiv = document.getElementById('response');
            
            responseDiv.innerHTML = 'Processing...';
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt })
                });
                
                const data = await response.json();
                
                if (data.html) {
                    responseDiv.innerHTML = data.html;
                } else if (data.error) {
                    responseDiv.innerHTML = `Error: ${data.error}`;
                }
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
            }
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
