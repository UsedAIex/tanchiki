import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from .db_session import SqlAlchemyBase
from wtforms import PasswordField, SubmitField
from flask_login import UserMixin

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                       primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)