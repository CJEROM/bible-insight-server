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
@app.route("/info/<translation>/books")
def get_books_for_translation(translation):
    search = Search()
    search.init_filter(is_active=False)
    search.update_filter("translations", translation, True)
    filters = search.get_filter()
    formatted_filters = {}
    for filter_type, filter_data in filters.items():
        print(filter_type, filter_data)

    return jsonify(filters)

@app.route("/info/translations")
def get_translations():
    search = Search()
    filters = search.get_filter("translations")
    return jsonify(filters)

@app.route("/search/<word>")
def search_word(word):
    return f"Search for word: {word}"

@app.route("/search/filter/<action>")
def adjust_search_filter(action):
    return f"Adjust search filter: {action}"

if __name__ == "__main__":
    host_address = "0.0.0.0"
    host_port = 8000
    print(f"✅ Starting Flask server on http://{host_address}:{host_port} ...")
    app.run(host=host_address, port=host_port, debug=True, use_reloader=False)