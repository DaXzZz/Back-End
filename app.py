from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, errors

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://mongo:mongo@cluster0.bll8kuf.mongodb.net/?retryWrites=true&w=majority")
db = client["products"]
pd_info_collection = db["pd_info"]

@app.route("/")
def greet():
    return "Welcome to Product Management API"

@app.route("/products", methods=["GET"])
def get_all_products():
    try:
        products = pd_info_collection.find()
        return jsonify([product for product in products]), 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products/<string:_id>", methods=["GET"])
def get_product(_id):
    try:
        product = pd_info_collection.find_one({'_id': _id})
        if product:
            return jsonify(product), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products", methods=["POST"])
def create_product():
    try:
        data = request.get_json()
        data['_id'] = data.pop('ProductId')  

        if pd_info_collection.find_one({'_id': data['_id']}):
            return jsonify({"error": "ID already exists"}), 400 

        result = pd_info_collection.insert_one(data)
        if result.inserted_id:
            product = pd_info_collection.find_one({'_id': data['_id']})
            return jsonify(product), 201
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/products/<string:_id>", methods=["PUT"])
def update_product(_id):
    try:
        data = request.get_json()
        result = pd_info_collection.update_one({'_id': _id}, {'$set': data})
        if result.matched_count:
            product = pd_info_collection.find_one({'_id': _id})
            return jsonify(product), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products/<string:_id>", methods=["DELETE"])
def delete_product(_id):
    try:
        result = pd_info_collection.delete_one({'_id': _id})
        if result.deleted_count:
            return jsonify({"message": "Product deleted successfully"}), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
