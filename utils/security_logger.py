from flask import request

from extensions import db
from models import SecurityLog


def log_security_event(user_email, activity):

    log = SecurityLog(
        user_email=user_email,
        activity=activity,
        ip_address=request.remote_addr
    )

    db.session.add(log)
    db.session.commit()