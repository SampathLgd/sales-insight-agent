import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any

# Load API key from .env file
load_dotenv()

# Configure the client to use OpenRouter (or any OpenAI-compatible API)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={"HTTP-Referer": "http://localhost:5000", "X-Title": "Sales Agent"},
)

# This reference date is set to match the latest data from the live API.
REFERENCE_TODAY_DATE = "2025-11-09"

def get_date_range_from_question(question: str) -> Dict[str, str]:
    """
    Uses an LLM to parse a natural language question into a structured date range.
    
    Args:
        question: The user's natural language question.

    Returns:
        A dictionary with "start_date" and "end_date" in YYYY-MM-DD format.
    """
    print(f"[LLMService] Parsing date for: '{question}'")
    
    system_prompt = f"""
    You are a date parsing assistant. Your task is to analyze the user's question
    and return a JSON object with a 'start_date' and 'end_date' in 'YYYY-MM-DD' format.
    
    The current date is: {REFERENCE_TODAY_DATE}.
    
    - "yesterday": Should be "2025-11-08" to "2025-11-08".
    - "today": Should be "2025-11-09" to "2025-11-09".
    - "last week": Should be the full week, from Monday "2025-10-27" to Sunday "2025-11-02".
    - "this month": Should be "2025-11-01" to "2025-11-09".
    
    If no specific date is mentioned (e.g., "show me top products"), assume "today".
    Return ONLY the JSON object.
    """
    
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku", # A fast and capable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            response_format={"type": "json_object"}
        )
        
        date_range_str = response.choices[0].message.content
        return json.loads(date_range_str)
        
    except Exception as e:
        print(f"[LLMService] Error parsing date: {e}")
        # Fallback to "today" if parsing fails
        return {"start_date": REFERENCE_TODAY_DATE, "end_date": REFERENCE_TODAY_DATE}

def generate_sales_summary(processed_data: Dict[str, Any]) -> str:
    """
    Uses an LLM to generate a natural language summary from processed data.
    
    Args:
        processed_data: The aggregated data dictionary from process_orders.
        
    Returns:
        A string of HTML formatted to be displayed to the user.
    """
    print("[LLMService] Generating final summary...")
    
    data_json = json.dumps(processed_data, indent=2)
    
    # This strict, data-only prompt prevents the LLM from hallucinating
    # or getting confused by the original question.
    system_prompt = f"""
    You are a data-to-text robot. Your ONLY task is to present the JSON data below
    in a clear, human-readable HTML format.
    
    **CRITICAL RULES:**
    1.  **ONLY USE THE JSON DATA PROVIDED.** Do not invent, add, or change any numbers.
    2.  **CURRENCY:** All monetary values are in cents. You MUST divide them by 100 and present them as dollars (e.g., 3372 cents is $33.72).
    3.  **FORMAT:** Use <p> tags for sentences and <ul>/<li> tags for lists.
    4.  **NO DATA:** If "total_revenue" is 0 and "total_orders" is 0, your ONLY response MUST be: 
        "<p>Unfortunately, there is no sales data available for the period from {processed_data['start_date']} to {processed_data['end_date']}.</p>"
    5.  **DATA EXISTS:** If "total_revenue" or "total_orders" is greater than 0:
        -   Start with: "<p>Here is the sales summary for {processed_data['start_date']} to {processed_data['end_date']}:</p>"
        -   Report the "total_revenue" (as dollars) and "total_orders" in a <ul>.
        -   If the "top_selling_items" list is not empty, add a heading "<p><strong>Top Selling Items:</strong></p>" and list them in a <ul>.
        -   If the "top_customers" list is not empty, add a heading "<p><strong>Top Customers:</strong></p>" and list them in a <ul>.
    
    **DATA TO REPORT:**
    {data_json}
    """
    
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Please generate the HTML response based on the data provided in your system prompt."}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"[LLMService] Error generating summary: {e}")
        return "<p>Sorry, I encountered an error while generating the summary.</p>"