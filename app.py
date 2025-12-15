from flask import Flask

# Create a Flask web server instance
app = Flask(__name__)

# Define a route for the homepage ('/')
@app.route('/')
def hello_world():
    # Return a string to be displayed in the browser
    return 'Hello, Render! This is my first simple Flask app.'

# This is often used for running locally, but Render will use the Procfile
if __name__ == '__main__':
    # Use 0.0.0.0 to listen on all public IPs, and use the PORT environment variable
    # provided by Render when deploying
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  
