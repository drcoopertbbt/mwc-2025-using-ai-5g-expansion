from flask import Flask, render_template
import json
import os

app = Flask(__name__, template_folder='templates')

def load_tickets():
    kb_path = os.path.join(os.path.dirname(__file__), 'data/knowledge_base/support_articles.json')
    with open(kb_path, 'r') as f:
        data = json.load(f)
        return data['support_tickets']

@app.route('/')
def simulator():
    tickets = load_tickets()
    return render_template('simulator.html', tickets=tickets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
