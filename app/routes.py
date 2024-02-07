from flask import request
from app import app, db
from app.models import User
from app.auth import basic_auth, token_auth


# USER ENDPOINTS 
@app.route("/token")
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return {"token":token,
            "tokenExpiration":user.token_expiration}

@app.route("/users/me")
@token_auth.login_required
def get_me():
    current_user = token_auth.current_user()
    return current_user.to_dict()


# Create New User
@app.route('/users', methods=['POST'])
def create_user():
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    
    data = request.json

    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    check_users = db.session.execute(db.select(User).where( (User.username==username) | (User.email==email) )).scalars().all()
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400

    new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
    return new_user.to_dict(), 201

# Update
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_user(user_id):
    if not request.is_json:
        return {"error": "your content type must be application/json !"}, 400
    user = db.session.get(User, user_id)
    if user is None:
        return {"error": f"User with {user_id} does not exist"},404
    current_user = token_auth.current_user()
    if user is not current_user:
        return {"error":"You cannot change this user as you are not them!"} ,403
    data = request.json
    user.update(**data)
    return user.to_dict()


# Delete
@app.route("/users/<int:user_id>", methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    current_user = token_auth.current_user()
    if user is None:
        return {"error":f"User with {user_id} not found!"},404
    if user is not current_user:
        return {"error":"You cant do that, delete yourself only"}, 403
    user.delete()
    return{"success":f"{user.username} has been deleted!"}

