from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace 'your_username', 'your_password', 'your_database' with your MySQL credentials
DATABASE_URI = 'mysql://root:root@localhost:3306/flask-app'

# Create Flask application
app = Flask(__name__)
# CORS(app)
# allow only angular local domain
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"], "allow_headers": "*"}})

# CORS(app, resources={r"/*": {"origins": "*"}})

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URI, echo=True)  # Set echo=True to see SQL queries

# Create a sessionmaker object
Session = sessionmaker(bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Define Product class as an ORM model
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer(), nullable=True)
    minimum_quantity = Column(Integer(), nullable=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

# Create tables (optional, if tables do not exist)
# Base.metadata.create_all(engine)


# ----------------------------AUTH START----------------------------



@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    session = Session()
    existing_user = session.query(User).filter_by(email=data['email']).first()
    if existing_user:
        session.close()
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(email=data['email'], password=data['password'])
    session.add(new_user)
    session.commit()
    session.close()

    return jsonify({'message': 'User registered successfully', 'success': True}), 201

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    session = Session()
    user = session.query(User).filter_by(email=data['email']).first()
    session.close()

    if not user or user.password != data['password']:
        return jsonify({'error': 'Invalid email or password', 'success': False}), 401

    return jsonify({'message': 'Login successful', 'success': True})



# ----------------------------AUTH ENDS----------------------------



# Route to fetch all products
@app.route('/product', methods=['GET'])
def get_products():
    session = Session()
    products = session.query(Product).all()
    session.close()

    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': product.quantity,
            'minimum_quantity': product.minimum_quantity
        }
        product_list.append(product_data)
    
    return jsonify({'products': product_list})




# Route to create a new product
@app.route('/product/create', methods=['POST'])
def create_product():
    data = request.json
    if not data or 'name' not in data or 'price' not in data or 'quantity' not in data or 'minimum_quantity' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    new_product = Product(name=data['name'], price=data['price'], quantity=data['quantity'], minimum_quantity=data['minimum_quantity'])
    
    session = Session()
    session.add(new_product)
    session.commit()
    
    product_data = {
        'id': new_product.id,
        'name': new_product.name,
        'price': float(new_product.price),
        'quantity': new_product.quantity,
        'minimum_quantity': new_product.minimum_quantity
    }
    session.close()
    
    return jsonify({'product': product_data}), 201

# Route to update a product
@app.route('/product/update/<int:product_id>', methods=['PUT', 'OPTIONS'])
def update_product(product_id):
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    session = Session()
    product = session.query(Product).get(product_id)
    
    if not product:
        session.close()
        return jsonify({'error': 'Product not found'}), 404

    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'quantity' in data:
        product.quantity = data['quantity']

    session.commit()
    
    product_data = {
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'quantity': product.quantity,
    }
    session.close()
    
    return jsonify({'product': product_data})

# Route to delete a product
@app.route('/product/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    session = Session()
    product = session.query(Product).get(product_id)
    
    if not product:
        session.close()
        return jsonify({'error': 'Product not found'}), 404

    session.delete(product)
    session.commit()
    session.close()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)