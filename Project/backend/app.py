from flask import Flask

app = Flask(__name__)

@app.route("/api/health")
def health_check():
    return {"status": "Pulse Net backend is running"}

@app.route("/api")
def api_home():
    return {"message": "Welcome to the Pulse Net API"}

if __name__ == "__main__":
    app.run(debug=True)