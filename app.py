from flask import Flask, request, jsonify
from extractor import *

app = Flask(__name__)

# Example function from your Python script
def process_extractor(url, fields):
    #url = 'https://webscraper.io/test-sites/e-commerce/static'
    #fields=['Name of item', 'Price']

    try:
        # # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Scrape data
        raw_html = fetch_html_selenium(url)
    
        markdown = html_to_markdown_with_readability(raw_html)
        
        # Save raw data
        save_raw_data(markdown, timestamp)

        # Create the dynamic listing model
        DynamicListingModel = create_dynamic_listing_model(fields)

        # Create the container model that holds a list of the dynamic listing models
        DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
        
        # Format data
        formatted_data, token_counts = format_data(markdown, DynamicListingsContainer,DynamicListingModel,"Groq Llama3.1 70b")  # Use markdown, not raw_html
        print(formatted_data)
        # Save formatted data
        save_formatted_data(formatted_data, timestamp)

        # Convert formatted_data back to text for token counting
        formatted_data_text = json.dumps(formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data) 
        
        
        # Automatically calculate the token usage and cost for all input and output
        input_tokens, output_tokens, total_cost = calculate_price(token_counts, "Groq Llama3.1 70b")
        print(f"Input token count: {input_tokens}")
        print(f"Output token count: {output_tokens}")
        print(f"Estimated total cost: ${total_cost:.4f}")

        return formatted_data
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# API endpoint
@app.route('/process', methods=['POST'])
def process_data():
    # Get the input data from the request
    data = request.json
    url = data.get('url')
    fields = data.get('fields')
    
    # Process the data using your script
    result = process_extractor(url, fields)

    # Return the result as JSON
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Exposes the API on port 5000
