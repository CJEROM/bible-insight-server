from flask import Flask, jsonify
import sqlite3
import json
import psycopg2

from tokeniser.assembler import Assembler

app = Flask(__name__)

@app.route("/init_database") 
def get_data():
    return "Empty API Call"

@app.route("/read/<translation>/<ref>")
def get_assembled_ref(translation, ref):
    scripture = Assembler(translation_id=translation, ref=ref)
    scripture.add_detail()
    print(scripture.get_details())
    return jsonify(scripture.get_details())

if __name__ == "__main__":
    host_address = "localhost"
    host_port = 8000
    print(f"✅ Starting Flask server on http://{host_address}:{host_port} ...")
    app.run(host=host_address, port=host_port, debug=True, use_reloader=False)