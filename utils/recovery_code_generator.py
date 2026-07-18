import secrets
import string

from extensions import db
from models import RecoveryCode


def generate_recovery_codes(user_id):

    # Delete any existing unused codes
    RecoveryCode.query.filter_by(
        user_id=user_id
    ).delete()

    characters = string.ascii_uppercase + string.digits

    generated = []

    for _ in range(10):

        while True:

            code = (
                "".join(secrets.choice(characters) for _ in range(4))
                + "-"
                + "".join(secrets.choice(characters) for _ in range(4))
            )

            exists = RecoveryCode.query.filter_by(
                recovery_code=code
            ).first()

            if not exists:
                break

        recovery = RecoveryCode(
            user_id=user_id,
            recovery_code=code,
            is_used=False
        )

        db.session.add(recovery)

        generated.append(code)

    db.session.commit()

    return generated