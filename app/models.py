from datetime import datetime

from app import db, login_manager

from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )


class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default='user'
    )

    avatar = db.Column(
        db.String(255),
        default='default.png'
    )

    bio = db.Column(
        db.Text,
        default='Cybersecurity user'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):

        return (
            f"User('{self.username}', "
            f"'{self.email}')"
        )


class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    encrypted_content = db.Column(
        db.Text,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class AuditLog(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    action = db.Column(
        db.String(255),
        nullable=False
    )

    ip_address = db.Column(
        db.String(100)
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )