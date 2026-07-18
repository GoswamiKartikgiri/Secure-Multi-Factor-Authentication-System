import os
import pyotp
import qrcode
from flask import current_app


def generate_totp_secret():
    """
    Generate a unique TOTP secret for each user.
    """
    return pyotp.random_base32()


def generate_qr_code(user_email, secret):
    """
    Generate QR Code for Google Authenticator.
    """

    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name="2FA Authentication System"
    )

    # Absolute path to the static/qrcodes folder
    qr_folder = os.path.join(
        current_app.root_path,
        "static",
        "qrcodes"
    )

    # Create the folder if it doesn't exist
    os.makedirs(qr_folder, exist_ok=True)

    filename = f"{user_email.replace('@', '_')}.png"

    filepath = os.path.join(qr_folder, filename)

    img = qrcode.make(totp_uri)
    img.save(filepath)

    # Return the path used by the browser
    return f"static/qrcodes/{filename}"