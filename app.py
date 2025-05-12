from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app)

DB_HOST = "34.198.77.142"
DB_NAME = "mi_basedatos"
DB_USER = "admin"
DB_PASS = "adminpass"

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/people', methods=['GET'])
def get_people():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, name FROM people ORDER BY id;")
    people = [{"id": row["id"], "name": row["name"]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(people)

@app.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING id;", (name,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "name": name}), 201

@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM people WHERE id = %s;", (person_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Person with ID {person_id} deleted"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
