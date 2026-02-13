from flask import Flask, render_template

# Create a Flask web server instance
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Use 0.0.0.0 to listen on all public IPs, and use the PORT environment variable
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
