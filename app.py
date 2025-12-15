from flask import Flask
import requests as r
# Create a Flask web server instance
app = Flask(__name__)
btu="https://api.telegram.org/"
# Define a route for the homepage ('/')
@app.route('/see/<path:token>')
def hello_world(token):
    # Return a string to be displayed in the browser
    print(f"{btu}{token}")
    a=r.get(f"{btu}{token}")
    return a.text
    
@app.route('/')
def hello_worl():
    return 'Hello, Render! This is my first simple Flask app.'
# This is often used for running locally, but Render will use the Procfile
if __name__ == '__main__':
    # Use 0.0.0.0 to listen on all public IPs, and use the PORT environment variable
    # provided by Render when deploying
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  
