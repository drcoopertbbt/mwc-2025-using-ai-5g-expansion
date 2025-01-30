# Industry Report Knowledge Base Emulator

A RAG-enabled Industry Report Analysis system that provides market insights and trend analysis using AI.

## Project Structure

```
Industry-Report-Knowledge-Base-Emulator/
├── src/
│   ├── app.py                 # Main Flask application
│   └── data/
│       ├── knowledge_base/    # Industry reports and market data
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
- The interface allows you to submit industry analysis queries
- Responses are generated using the knowledge base

## Features

- RAG (Retrieval-Augmented Generation) system
- Industry reports knowledge base
- Markdown rendering for formatted responses
- Local data storage for prompts and responses
- Simple web interface for interaction

## Testing

You can test the system with queries related to:
- Market size and growth analysis
- Industry trends and patterns
- Investment opportunities
- Strategic recommendations

Example query: "What are the key trends in the 5G infrastructure market?"

## Data Storage

The application stores:
- User queries in `src/data/prompts/`
- System responses in `src/data/responses/`
- RAG interactions in `src/data/rag-database/`

This data persistence allows for analysis of market trends and system performance.

## Knowledge Base

The knowledge base (`src/data/knowledge_base/support_articles.json`) contains market data for:
- Market size and growth metrics
- Industry sector analysis
- Investment trends
- Technology adoption patterns

You can extend the knowledge base by adding new industry reports and market data to the JSON file.

# Once You've Installed Everything

```bash
source venv/bin/activate && python src/app.py
