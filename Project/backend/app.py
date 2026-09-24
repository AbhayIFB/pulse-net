# Import Flask, which we use to create our web application
from flask import Flask

# Import the network discovery function from network.py
from network import discover_devices

# Create a Flask application instance
app = Flask(__name__)



# Define an API endpoint for checking whether the backend is running
@app.route("/api/health")
def health_check():

    # Return a JSON response confirming that the backend is running
    return {"status": "Pulse Net backend is running"}



# Define the main endpoint for the Pulse Net API
@app.route("/api")
def api_home():

    # Return a welcome message from the API
    return {"message": "Welcome to the Pulse Net API"}



# Define an API endpoint for discovering devices on the network
@app.route("/api/devices")
def get_devices():
    # Scan the local network and retrieve the discovered devices
    devices = discover_devices()

    # Return the discovered devices as JSON
    return {"devices": devices}



# Only run the Flask development server when this file is executed directly
if __name__ == "__main__":

    # Start the Flask development server with debug mode enabled
    app.run(debug=True)