from flask_restful import Resource, Api
from app import app, db, User

api = Api(app)

class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        user_list = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        return {'users': user_list}

api.add_resource(UserListResource, '/api/users')
