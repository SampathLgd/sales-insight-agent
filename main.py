import api_client
import data_processor
import llm_service
import json
import re

def strip_html(text):
    """Removes simple HTML tags from the AI's response for clean CLI output."""
    return re.sub(r'<[^>]+>', '', text).replace('&nbsp;', ' ')

def main_cli():
    """
    Main function for the command-line interface.
    """
    print("Welcome to the Sales Insight Agent!")
    print("Type your question (e.g., 'What were our sales yesterday?')")
    print("Type 'exit' to quit.")
    
    while True:
        try:
            question = input("\n> ")
            if question.lower() == 'exit':
                print("Goodbye!")
                break
                
            # Step 1: Parse date from question
            date_range = llm_service.get_date_range_from_question(question)
            if not date_range or 'start_date' not in date_range or 'end_date' not in date_range:
                print("Sorry, I couldn't understand the date in your question.")
                continue
            
            # Step 2: Fetch API data (with Caching)
            orders_data = api_client.fetch_orders()
            if orders_data is None:
                print("Sorry, I couldn't fetch the sales data.")
                continue
                
            # Step 3: Process data in Python for accuracy
            processed_data = data_processor.process_orders(
                orders_data, 
                date_range['start_date'], 
                date_range['end_date']
            )
            
            # Step 4: Use LLM to generate the final answer
            # Note: This calls the LLM service which now only accepts processed_data
            html_summary = llm_service.generate_sales_summary(processed_data)
            
            # Clean the HTML for a tidy console experience
            cli_summary = strip_html(html_summary)
            
            print(f"\n{cli_summary}\n")
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main_cli()