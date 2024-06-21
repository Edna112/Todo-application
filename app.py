from flask import Flask,render_template,request,redirect,url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_migrate import Migrate

app = Flask(__name__)
# /// = relative path, //// = absolute path

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate()

db = SQLAlchemy()
db.init_app(app)
migrate.init_app(app, db)

class ToDo(db.Model):
    __tablename__ = 'todo'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    complete= db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'complete': self.complete,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    

@app.route('/')
def home():
    todo =  todo.query.all()
    return render_template('base.html',todo = todo)

@app.route("/add", methods=["POST"])
def add():
    try:
        data = request.get_json()
        new_todo = ToDo(title=data['title'], description=data['description'], complete=data['complete'])
        db.session.add(new_todo) 
        db.session.commit()
        return make_response(jsonify({'message': 'Todo created'}), 201)
    except Exception as e:
        print(f"Error creating todo: {e}")
        return make_response(jsonify({'message': f'error creating todo: {e}'}), 500)
    

@app.route("/todo", methods=["GET"])
def get_todos():
    try:
        todos =  ToDo.query.all()
        return make_response(jsonify([todo.json() for todo in todos]), 200)
    except Exception as e:
        print(f"Error fetching todo: {e}")
        return make_response(jsonify({'message': f'error fetching todo: {e}'}), 500) #error fetching todo
    
@app.route("/todo/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    try:
        todo =  ToDo.query.filter_by(id = todo_id).first()
        if todo:
            return make_response(jsonify({'todo': todo.json()}), 200)
        return make_response(jsonify({'message': 'todo not found'}), 404)
    except Exception as e:
        print(f"Error fetching todo: {e}")
        return make_response(jsonify({'message': f'error fetching todo: {e}'}), 500)

    
@app.route('/todo/<int:id>', methods=['PUT'])
def update_todo(id):
    try:
        todo = ToDo.query.filter_by(id=id).first()
        if todo:
            data = request.get_json()
            todo.title = data['title']
            todo.description = data['description']
            todo.complete = data['complete']
            db.session.commit()
            return make_response(jsonify({'message': 'Todo updated', 'updated todo': todo.json()}), 200)
        return make_response(jsonify({'message': 'Todo not found'}), 404)
    except Exception as e:
        print(f"Error updating todo: {e}")
        return make_response(jsonify({'message': 'error updating todo'}), 500)
         
@app.route('/todo/<int:id>', methods=['DELETE'])
def delete_todo(id):
    try:
        todo = ToDo.query.filter_by(id=id).first()
        if todo:
            db.session.delete(todo)
            db.session.commit()
            return make_response(jsonify({'message': 'todo deleted'}), 200)
        return make_response(jsonify({'message': 'todo not found'}), 404)
    except Exception as e:
        print(f"Error deleting todo: {e}")
        return make_response(jsonify({'message': 'error deleting todo'}), 500)

if __name__ =='__main__':
    with app.app_context():
     db.create_all()
    app.run(debug=True)