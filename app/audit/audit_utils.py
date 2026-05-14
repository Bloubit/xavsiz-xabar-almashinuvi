from flask import request

from app import db

from app.models import AuditLog


def log_action(user_id, action):

    log = AuditLog(

        user_id=user_id,

        action=action,

        ip_address=request.remote_addr
    )

    db.session.add(log)

    db.session.commit()