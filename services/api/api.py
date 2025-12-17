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
    filters = search.get_filter("books")
    formatted_filters = []
    # Return filters as {value, label}
    for book_code, book_data in filters.items():
        if book_data.get("active"):
            formatted_filters.append(
                {   
                    "label": book_data.get("name"),
                    "value": book_code
                }
            )
        print(book_code, book_data)

    return jsonify(formatted_filters)

@app.route("/info/translations")
def get_translations():
    search = Search()
    filters = search.get_filter("translations")
    formatted_filters = []
    # Return filters as {value, label}
    for translation_id, translation_data in filters.items():
        if translation_data.get("active"):
            name = translation_data.get("name")
            code = translation_data.get("code")
            translation_label = f"{name} [{code}]"
            formatted_filters.append(
                {
                    "label": translation_label,
                    "value": translation_id
                }
            )
        print(translation_id, translation_data)
    return jsonify(formatted_filters)

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