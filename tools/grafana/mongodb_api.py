#!/usr/bin/env python3
from flask import Flask, jsonify, request
from pymongo import MongoClient
import json
import bson.json_util as json_util

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['sqlmap_db']
collection = db['sqlmap']

@app.route('/api/sqlmap', methods=['GET'])
def get_sqlmap_data():
    # Get data from MongoDB
    data = list(collection.find())
    
    # Convert MongoDB data to JSON
    json_data = json.loads(json_util.dumps(data))
    
    return jsonify(json_data)

@app.route('/api/sqlmap/count', methods=['GET'])
def get_sqlmap_count():
    # Get count from MongoDB
    count = collection.count_documents({})
    
    return jsonify({"count": count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)