from flask import Flask, jsonify
import sqlite3
import json
import psycopg2

from tokeniser.assembler import Assembler
from utilities.search import Search

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

# Currently used as a way to present navigation options to user, by instantiationg disposable Search object
@app.route("/info/scripture_filters")
def get_scripture_params():
    search = Search()
    filters = search.get_filter()
    return jsonify(filters)

@app.route("/search/<word>")
def search_word(word):
    return f"Search for word: {word}"

@app.route("/search/filter/<action>")
def adjust_search_filter(action):
    return f"Adjust search filter: {action}"

if __name__ == "__main__":
    host_address = "localhost"
    host_port = 8000
    print(f"✅ Starting Flask server on http://{host_address}:{host_port} ...")
    app.run(host=host_address, port=host_port, debug=True, use_reloader=False)