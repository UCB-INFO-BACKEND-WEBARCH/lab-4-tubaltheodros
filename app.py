"""
Week 4
Complete TODO 1-5 in order.
"""

from flask import Flask, request, jsonify

# TODO 1: Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# TODO 1: Add configuration and create db instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db = SQLAlchemy(app)


# ── TODO 2: Create TodoModel ──────────────────────────────────────────────────
# Replace the in-memory list below with a SQLAlchemy model.
# Hint: refer to your Book API code from class.

class TodoModel(db.Model):
    __tablename__ = "todos"
 
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    status      = db.Column(db.String(20), default="pending")
    priority    = db.Column(db.String(20), default="medium")
    # TODO 5 — foreign key to categories
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
 
    def to_dict(self):
        return {
            "id":          self.id,
            "title":       self.title,
            "description": self.description,
            "status":      self.status,
            "priority":    self.priority,
            "category_id": self.category_id,
        }


# ── TODO 5: CategoryModel (leave commented out until TODO 5) ─────────────────
class CategoryModel(db.Model):
    __tablename__ = "categories"
 
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    todos = db.relationship('TodoModel', backref='category', lazy=True)
 
    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "todo_count": len(self.todos),
        }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/api/todos', methods=['GET'])
def get_todos():
    query = TodoModel.query
 
    status      = request.args.get('status')
    priority    = request.args.get('priority')
    category_id = request.args.get('category_id')
 
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category_id:
        query = query.filter_by(category_id=int(category_id))
 
    todos = query.all()
    return jsonify([t.to_dict() for t in todos]), 200
 
 
@app.route('/api/todos/<int:id>', methods=['GET'])
def get_todo(id):
    todo = db.get_or_404(TodoModel, id)
    return jsonify(todo.to_dict()), 200
 
 
@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
 
    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400
 
    todo = TodoModel(
        title       = data['title'],
        description = data.get('description'),
        status      = data.get('status', 'pending'),
        priority    = data.get('priority', 'medium'),
        category_id = data.get('category_id'),
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201
 
 
@app.route('/api/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    todo = db.get_or_404(TodoModel, id)
    data = request.get_json()
 
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'status' in data:
        todo.status = data['status']
    if 'priority' in data:
        todo.priority = data['priority']
    if 'category_id' in data:
        todo.category_id = data['category_id']
 
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
 
@app.route('/api/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = db.get_or_404(TodoModel, id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted"}), 200


# ── TODO 5: Category Routes (leave commented out until TODO 5) ───────────────
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = CategoryModel.query.all()
    return jsonify([c.to_dict() for c in categories]), 200
 
 
@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
 
    if not data or not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
 
    category = CategoryModel(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201
 
 
@app.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = db.get_or_404(CategoryModel, id)
    return jsonify(category.to_dict()), 200
 
 
# TODO 4 — Initialize the database
with app.app_context():
    db.create_all()
 
if __name__ == '__main__':
    app.run(debug=True)