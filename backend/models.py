from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed password

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        """Verify password"""
        return bcrypt.check_password_hash(self.password, raw_password)


# class GeneratedDoc(db.Model):
#     __tablename__ = "generated_docs"

#     id = db.Column(db.Integer, primary_key=True)
#     row_id = db.Column(db.Integer, nullable=False)  # Excel row id
#     file_name = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class GeneratedDoc(db.Model):
#     __tablename__ = "generated_docs"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#     row_id = db.Column(db.Integer, nullable=False)
#     file_name = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     user = db.relationship("User", backref="generated_docs")


class UserFile(db.Model):
    __tablename__ = "user_files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)  # optional if downloaded
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    source_type = db.Column(db.String(20), default="uploaded")  # uploaded / downloaded
    category = db.Column(db.String(50), nullable=False)


    user = db.relationship("User", backref="files")


class GeneratedDoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    row_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)  # Store bytes here
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="generated_docs")

