import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

# Veri tabanı bağlantısı
uri = os.getenv("MONGO_ATLAS_URI")
client = MongoClient(uri)
db = client.tododb.todo # tododb: veri tabanı ismi, todo: collection name

app = Flask(__name__)
app.secret_key = "çok gizli key"
CORS(app)

@app.route('/')  # http://www.abc.com/
def home():
    mesaj = """
    <h1> Todo Web API </h1>
    <ol>
    <li>/api/todos hem get hem post request</li>
    <li>/api/todo/id: belirli bir id kaydını alma</li>
    <li>/api/update put request</li>
    <li>/api/delete delete request</li>
    </ol>
    """
    return mesaj

@app.route('/api/todos', methods = ['GET', 'POST'])
def todos():
    if request.method == 'POST':
        _name = request.json['name']
        _completed = request.json['completed']
        if _name and _completed:
            db.insert_one({"name": _name, "completed" : _completed})
            resp = jsonify('Todo başarıyla eklendi!')
            resp.status_code = 200
            return resp
        else:
            return not_found()

    else:
        todos = []
        for todo in db.find():
            todos.append({"_id": str(todo['_id']), "name": todo['name'], "completed": todo['completed']})       
        return jsonify(todos)
        # todos = db.find()
        # return dumps(todos, ensure_ascii=False)

@app.route('/api/todo/<id>')
def todo(id):
    todo = db.find_one({'_id': ObjectId(id)})
    return jsonify({"_id": str(todo['_id']), "name": todo['name'], "completed": todo['completed']})
    #return dumps(todo, ensure_ascii=False)

@app.route('/api/update', methods=['PUT'])
def updated_todo():    
    _id = request.json['_id']
    _name = request.json['name']
    _completed = request.json['completed']

    if _name and _completed and _id and request.method == 'PUT': 
        db.find_one_and_update({'_id': ObjectId(_id)},
                                 {'$set': {'name': _name, 'completed': _completed}}) 
        resp = jsonify('Todo başarıyla güncellendi!')
        resp.status_code = 200
        return resp
        """
        db.update_one({'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(
            _id)}, {'$set': {'name': _name, 'completed': _completed}})
        """
    else:
        return not_found()

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_todo(id):
    db.find_one_and_delete({'_id': ObjectId(id)})
    resp = jsonify('Todo başarıyla silindi!')
    resp.status_code = 200
    return resp

    
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

if __name__ == "__main__":
    app.run(debug=True)
