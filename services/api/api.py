from flask import Flask, jsonify
import sqlite3
import json
import psycopg2

app = Flask(__name__)

@app.route("/init_database") 
def get_data():
    return "Empty API Call"

if __name__ == "__main__":
    print("✅ Starting Flask server on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)