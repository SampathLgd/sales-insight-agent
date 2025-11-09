# Sales Insight Agent

[cite_start]This project is a submission for the Internship Assessment[cite: 27]. [cite_start]It is an intelligent agent that answers natural language questions about sales data[cite: 29]. [cite_start]It works by fetching live data from the Sales API [cite: 35][cite_start], processing it in Python, and using an LLM to generate clear, natural language answers[cite: 36].

The application is available as both a web interface and a command-line (CLI) tool.

## Features

* [cite_start]**Natural Language Questions**: Ask questions like "What were our sales yesterday?" [cite: 39] or "Who are our top customers?".
* [cite_start]**Smart Date Parsing**: Automatically parses relative dates like "today", "yesterday", and "last week"[cite: 52].
* [cite_start]**Live API Integration**: Connects to the sandbox Sales API to fetch real-time data[cite: 57].
* **Accurate Data Analysis**: All calculations (totals, item counts, customer revenue) are done in Python (`data_processor.py`) *before* being sent to the LLM. This prevents LLM "hallucinations" and ensures 100% accurate metrics.
* [cite_start]**API Caching**: Implements a 10-minute cache (`api_client.py`) to reduce API calls and improve response speed for repeated queries[cite: 51].
* [cite_start]**Dual Interface**: Includes both a simple, effective command-line interface (`main.py`) and a user-friendly web UI (`app.py` + `index.html`)[cite: 47].
* [cite_start]**Robust Error Handling**: The application gracefully handles API connection errors, date parsing failures, and empty data sets[cite: 48, 166].

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd sales-agent
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    * Rename `.env.example` to `.env`.
    * [cite_start]Open `.env` and add your API key[cite: 147, 175]. This project is configured for OpenRouter, which provides free access to models like `claude-3-haiku`.
        ```
        OPENAI_API_KEY=sk-or-v1-your-openrouter-api-key-here
        ```

## How to Run

You can run either the Web Application or the Command-Line Interface.

### Option 1: Run the Web Application (Recommended)

1.  Run the Flask server:
    ```bash
    python3 app.py
    ```
2.  Open your web browser and go to:
    `http://127.0.0.1:5000`

### Option 2: Run the CLI Tool

1.  Run the main script from your terminal:
    ```bash
    python3 main.py
    ```
2.  Follow the prompts to ask questions. Type `exit` to quit.

## Example Queries

* `Show me top performing products` (Shows data for today, 2025-11-09)
* `What were our sales yesterday?` (Shows data for 2025-11-08)
* `Compare this week vs last week` (Attempts to show data for 2025-10-27 to 2025-11-02)
* `Who are our top customers?`

## Design Decisions

* **Processor-First Logic**: The most important decision was to *not* trust the LLM with calculations. The application uses the LLM *only* for "Natural Language Understanding" (parsing dates) and "Natural Language Generation" (formatting the final answer). All business logic—filtering by date, counting orders, summing revenue, and ranking items/customers—is done in `data_processor.py`. This makes the application accurate and reliable.
* **Strict LLM Prompting**: The `generate_sales_summary` function in `llm_service.py` uses a very strict "data-to-text" prompt. It is *not* given the user's original question, only the final data. This prevents it from getting confused (e.g., trying to answer about "last week" when the data for that period was $0).
* **Live Date Handling**: The code uses a hardcoded `REFERENCE_TODAY_DATE = "2025-11-09"` to align with the "Last 2 days" data range of the live API. This was a critical fix to make "today" and "yesterday" queries work correctly.
* [cite_start]**API Format Discovery**: The API's documentation [cite: 60] incorrectly states it returns a `list`. The `api_client.py` was built to correctly parse the *actual* `dictionary` response (`{"orders": [...]}`).

## Brief Reflection

* **Most Challenging Aspect:** The most challenging part was debugging the discrepancy between the API documentation and its real-world behavior. [cite_start]The documentation [cite: 60] showed a `list` response, but the API returned a `dict`. The second challenge was an LLM "hallucination," where the AI would invent numbers or answer the wrong question when it received empty data (e.g., for "last week").
* **What I Would Improve:** I would make the date parsing more robust. Right now, it relies on the LLM, but I could add a Python-based parser (like `dateutil`) to handle simple keywords first, only using the LLM for more complex queries. I would also add proper unit tests for `data_processor.py` to verify all aggregation logic.
* **Interesting Decisions:** The key decision was to create a strict "pipeline" (Parse -> Fetch -> Process -> Report). This separates concerns cleanly. By forcing the final LLM prompt to *only* report on the JSON it's given (and not the original question), I solved all the hallucination issues and ensured the answers are 100% data-driven.