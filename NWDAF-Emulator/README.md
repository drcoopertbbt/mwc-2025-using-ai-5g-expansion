# NWDAF Emulator

A RAG-enabled Network Data Analytics Function (NWDAF) emulator that provides network analytics and insights using AI.

## Project Structure

```
NWDAF-Emulator/
├── src/
│   ├── app.py                 # Main Flask application
│   └── data/
│       ├── knowledge_base/    # Network analytics knowledge base
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
- The interface allows you to submit network analytics queries
- Responses are generated using the knowledge base

## Features

- RAG (Retrieval-Augmented Generation) system
- Network analytics knowledge base
- Markdown rendering for formatted responses
- Local data storage for prompts and responses
- Simple web interface for interaction

## Testing

You can test the system with queries related to:
- Network load analysis
- Slice performance metrics
- Device connectivity patterns
- Network optimization recommendations

Example query: "What's the current load on the eMBB slice?"

## Data Storage

The application stores:
- User queries in `src/data/prompts/`
- System responses in `src/data/responses/`
- RAG interactions in `src/data/rag-database/`

This data persistence allows for analysis of network patterns and system performance.

## Knowledge Base

The knowledge base (`src/data/knowledge_base/support_articles.json`) contains analytics data for:
- eMBB (Enhanced Mobile Broadband)
- URLLC (Ultra-Reliable Low-Latency Communication)
- mMTC (Massive Machine Type Communication)

You can extend the knowledge base by adding new network analytics data to the JSON file.

# Once You've Installed Everything

```bash
source venv/bin/activate && python src/app.py
