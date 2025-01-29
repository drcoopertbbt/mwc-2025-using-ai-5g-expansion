# Support Ticket System Emulator

A RAG-enabled customer support system that uses a knowledge base to provide context-aware responses to customer queries.

## Project Structure

```
Support-Ticket-System-Emulator/
├── src/
│   ├── app.py                 # Main Flask application
│   └── data/
│       ├── knowledge_base/    # Knowledge base articles
│       ├── prompts/           # Stored user prompts
│       ├── responses/         # Stored system responses
│       └── rag-database/      # RAG interaction history
└── requirements.txt           # Python dependencies
```

## Local Development Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
cd src
python app.py
```

4. Access the application:
- Open http://localhost:8080 in your web browser
- The interface allows you to submit support queries
- Responses are generated using the knowledge base

## Features

- RAG (Retrieval-Augmented Generation) system
- Knowledge base with support articles
- Markdown rendering for formatted responses
- Local data storage for prompts and responses
- Simple web interface for interaction

## Testing

You can test the system with queries related to:
- Network connectivity issues
- Billing and payments
- Account management
- Product features
- Technical requirements

Example query: "How do I fix network connectivity issues?"

## Data Storage

The application stores:
- User queries in `src/data/prompts/`
- System responses in `src/data/responses/`
- RAG interactions in `src/data/rag-database/`

This data persistence allows for analysis of user interactions and system performance.

## Knowledge Base

The knowledge base (`src/data/knowledge_base/support_articles.json`) contains articles in the following categories:
- Networking
- Billing
- Account Management
- Product Features
- Technical Requirements

You can extend the knowledge base by adding new articles to the JSON file.


# Once You've Installed Everything

```bash
source venv/bin/activate && python src/app.py
```