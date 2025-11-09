from flask import Flask, render_template, request, jsonify
import traceback
import api_client
import data_processor
import llm_service

app = Flask(__name__)

@app.route("/")
def index():
    """Serves the main HTML page."""
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    """Handles the user's question from the web interface."""
    
    data = request.json
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Step 1: Call LLM to parse the date from the question
        date_range = llm_service.get_date_range_from_question(question)
        if not date_range or 'start_date' not in date_range or 'end_date' not in date_range:
            print(f"[App] LLM failed to parse date, got: {date_range}")
            return jsonify({"error": "Sorry, I couldn't understand the date in your question."}), 400

        # Step 2: Fetch data from the live API (uses caching)
        orders_data = api_client.fetch_orders()
        if orders_data is None:
            return jsonify({"error": "Sorry, I couldn't connect to the Sales API."})

        # Step 3: Process the data (filter by date, aggregate)
        processed_data = data_processor.process_orders(
            orders_data, 
            date_range['start_date'], 
            date_range['end_date']
        )

        # Step 4: Generate a natural language summary from the processed data
        # We pass only the data, not the original question, to prevent LLM hallucinations.
        summary = llm_service.generate_sales_summary(processed_data)

        # Send the final HTML answer back to the web page
        return jsonify({"answer": summary})

    except Exception as e:
        # Log the full error to the console for debugging
        print(f"Error in /ask route: {e}\n{traceback.format_exc()}")
        # Return a generic error message to the user
        return jsonify({"error": "Sorry, an unexpected internal error occurred."}), 500

if __name__ == "__main__":
    # Runs the Flask app on http://127.0.0.1:5000
    app.run(debug=True, port=5000)