from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user
import pyotp

from extensions import db
from models import User, RecoveryCode
from utils.qr_generator import generate_totp_secret, generate_qr_code
from utils.recovery_code_generator import generate_recovery_codes
from utils.security_logger import log_security_event

twofa = Blueprint("twofa", __name__)


@twofa.route("/setup-2fa")
@login_required
def setup_2fa():

    if not current_user.totp_secret:

        current_user.totp_secret = generate_totp_secret()
        db.session.commit()

    qr_path = generate_qr_code(
        current_user.email,
        current_user.totp_secret
    )

    return render_template(
        "setup_2fa.html",
        qr_path="/" + qr_path,
        secret=current_user.totp_secret
    )


@twofa.route("/verify-2fa", methods=["GET", "POST"])
@login_required
def verify_2fa():

    if request.method == "POST":

        otp = request.form.get("otp").strip()

        totp = pyotp.TOTP(current_user.totp_secret)

        if totp.verify(otp, valid_window=1):

            current_user.is_2fa_enabled = True
            db.session.commit()

            from utils.email_sender import send_email

            send_email(
            current_user.email,
            "Two-Factor Authentication Enabled",
            f"""
            Hello {current_user.full_name},

            Two-Factor Authentication has been enabled successfully.

            Your account is now more secure.

            Secure MFA System
            """
            )
            # Generate recovery codes
            recovery_codes = generate_recovery_codes(
                current_user.id
            )

            # Security logs
            log_security_event(
                current_user.email,
                "2FA Enabled"
            )

            log_security_event(
                current_user.email,
                "Recovery Codes Generated"
            )

            flash(
                "Two-Factor Authentication Enabled Successfully!",
                "success"
            )

            return render_template(
                "recovery_codes.html",
                recovery_codes=recovery_codes
            )

        log_security_event(
            current_user.email,
            "2FA Verification Failed"
        )

        flash(
            "Invalid OTP. Please try again.",
            "danger"
        )

    return render_template(
        "verify_2fa.html"
    )


@twofa.route("/recovery-login", methods=["GET", "POST"])
def recovery_login():

    if request.method == "POST":

        code = request.form.get(
            "recovery_code"
        ).strip().upper()

        recovery = RecoveryCode.query.filter_by(
            recovery_code=code,
            is_used=False
        ).first()

        if recovery:

            recovery.is_used = True
            db.session.commit()

            user = User.query.get(
                recovery.user_id
            )

            login_user(user)

            log_security_event(
                user.email,
                "Recovery Code Used"
            )

            flash(
                "Recovery code accepted. Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard.dashboard_page")
            )

        flash(
            "Invalid or already used recovery code.",
            "danger"
        )

    return render_template(
        "recovery_login.html"
    )