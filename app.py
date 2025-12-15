from flask import Flask, request, abort # Import 'request'
import requests as r
import os

# Create a Flask web server instance
app = Flask(__name__)
# Base URL for the Telegram Bot API (the actual endpoint, not your proxy's)
TELEGRAM_API_ROOT = "https://api.telegram.org/" 

# Modify the route to accept both GET and POST requests
@app.route('/see/<path:api_path>', methods=['GET', 'POST'])
def telegram_proxy(api_path):
    """
    Forwards the request to the Telegram Bot API using the original request method.
    """
    
    full_telegram_url = f"{TELEGRAM_API_ROOT}{api_path}"
    
    # 1. Determine the method (GET or POST)
    method = request.method 
    
    # 2. Get the data/files/JSON from the original request
    data = request.get_data()
    headers = {'Content-Type': request.content_type}
    
    try:
        # 3. Use requests.request() to perform the original method
        if method == 'POST':
            # POST requests typically send JSON/form data
            response = r.post(full_telegram_url, data=data, headers=headers)
        elif method == 'GET':
            # GET requests pass parameters in the URL
            response = r.get(full_telegram_url, params=request.args)
        else:
            # Handle other methods if necessary (though rare for Telegram)
            return "Method not supported by proxy", 400

        # Return the content, status code, and headers from the Telegram API
        return response.content, response.status_code, response.headers.items()
            
    except r.exceptions.RequestException as e:
        app.logger.error(f"Request failed: {e}")
        abort(500, description="Internal proxy error: Could not reach Telegram API.")

# ... (rest of your app.py remains the same) ...

# Your original root route:
@app.route('/')
def hello_worl():
    return 'Hello, Render! This is my first simple Flask app.'

# Your original run code:
if __name__ == '__main__':
    # Use 0.0.0.0 to listen on all public IPs, and use the PORT environment variable
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
