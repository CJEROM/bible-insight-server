from flask import Flask, jsonify
import sqlite3
import json

app = Flask(__name__)

@app.route("/geojson_all") 
def get_all_geojson(): 
    conn = sqlite3.connect("bibleData.db") 
    cursor = conn.cursor() 
    cursor.execute("SELECT file_content FROM Files WHERE type LIKE 'application/json'") # adjust table/column name 
    rows = cursor.fetchall() 

    features = [] 
    for row in rows: 
        geometry = json.loads(row[0]) 
        features.append({ 
            "type": "Feature", 
            "geometry": geometry, 
            "properties": {} 
        }) 
    
    feature_collection = {"type": "FeatureCollection", "features": features} 
    return jsonify(feature_collection)

@app.route("/geojson/<file_name>")
def get_geojson(file_name):
    conn = sqlite3.connect("bibleData.db")
    cursor = conn.cursor()

    # Use parameter substitution to avoid SQL injection
    cursor.execute(
        "SELECT file_content FROM Files WHERE type LIKE 'application/json' AND file_name = ?",
        (file_name,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"error": f"No GeoJSON found for '{file_name}'"}), 404

    features = []
    for row in rows:
        try:
            geometry = json.loads(row[0])
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {}
            })
        except Exception as e:
            print(f"Skipping bad row: {e}")

    feature_collection = {"type": "FeatureCollection", "features": features}
    return jsonify(feature_collection)


if __name__ == "__main__":
    print("✅ Starting Flask server on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)