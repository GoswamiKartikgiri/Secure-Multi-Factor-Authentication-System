from datetime import datetime, timedelta
import secrets
import pyotp

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from extensions import db, bcrypt

from models import (
    User,
    PasswordResetToken
)

from utils.security_logger import log_security_event

from utils.email_sender import (
    send_email,
    send_registration_email,
    send_login_email,
    send_account_locked_email,
    send_reset_password_email,
    send_password_changed_email,
    send_2fa_enabled_email,
    send_logout_email
)

auth = Blueprint(
    "auth",
    __name__
)
# =====================================================
# Register
# =====================================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        user = User(

            full_name=full_name,

            email=email,

            password=hashed_password

        )

        db.session.add(user)

        db.session.commit()

        # Security Log
        log_security_event(
            email,
            "User Registration"
        )

        # Registration Email
        send_email(

            user.email,

            "Registration Successful",

            f"""
Hello {user.full_name},

Your account has been created successfully.

Welcome to the Secure Multi-Factor Authentication System.

Thank you for registering.

Regards,
Security Team
"""
        )

        flash(

            "Registration Successful! Please Login.",

            "success"

        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


# =====================================================
# Login
# =====================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user:

            # -----------------------------
            # Account Lock Check
            # -----------------------------
            if (
                user.account_locked_until
                and
                user.account_locked_until > datetime.utcnow()
            ):

                flash(
                    "Account is locked. Try again after 15 minutes.",
                    "danger"
                )

                return redirect(
                    url_for("auth.login")
                )

            # -----------------------------
            # Correct Password
            # -----------------------------
            if bcrypt.check_password_hash(
                user.password,
                password
            ):

                user.failed_login_attempts = 0

                user.account_locked_until = None

                db.session.commit()

                log_security_event(
                    email,
                    "Login Successful"
                )

                # If 2FA Enabled
                if user.is_2fa_enabled:

                    session["temp_user_id"] = user.id

                    return redirect(
                        url_for("auth.login_2fa")
                    )

                # Normal Login
                login_user(user)

                # Login Email
                send_email(

                    user.email,

                    "Login Successful",

                    f"""
Hello {user.full_name},

A successful login to your account has been detected.

If this wasn't you, please change your password immediately.

Regards,
Security Team
"""
                )

                flash(
                    "Login Successful!",
                    "success"
                )

                return redirect(
                    url_for("dashboard.dashboard_page")
                )
            
                        # -----------------------------
            # Wrong Password
            # -----------------------------

            user.failed_login_attempts += 1

            if user.failed_login_attempts >= 5:

                user.account_locked_until = (
                    datetime.utcnow() + timedelta(minutes=15)
                )

                db.session.commit()

                log_security_event(
                    email,
                    "Account Locked (Too Many Failed Logins)"
                )

                # Account Locked Email
                send_email(

                    user.email,

                    "Security Alert - Account Locked",

                    f"""
Hello {user.full_name},

Your account has been locked because of too many failed login attempts.

The account will automatically unlock after 15 minutes.

If this was not you, please change your password immediately.

Regards,
Security Team
"""
                )

                flash(
                    "Too many failed login attempts. Account locked for 15 minutes.",
                    "danger"
                )

            else:

                db.session.commit()

                remaining = 5 - user.failed_login_attempts

                log_security_event(
                    email,
                    "Login Failed"
                )

                flash(
                    f"Invalid password. {remaining} attempt(s) remaining.",
                    "warning"
                )

            return redirect(
                url_for("auth.login")
            )

        flash(
            "User does not exist.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# =====================================================
# Login with 2FA
# =====================================================

@auth.route("/login-2fa", methods=["GET", "POST"])
def login_2fa():

    user_id = session.get("temp_user_id")

    if not user_id:

        return redirect(
            url_for("auth.login")
        )

    user = User.query.get(user_id)

    if request.method == "POST":

        otp = request.form.get("otp").strip()

        # -----------------------------
        # OTP Lock Check
        # -----------------------------

        if (
            user.otp_locked_until
            and
            user.otp_locked_until > datetime.utcnow()
        ):

            flash(
                "OTP verification locked for 15 minutes.",
                "danger"
            )

            return redirect(
                url_for("auth.login_2fa")
            )

        totp = pyotp.TOTP(
            user.totp_secret
        )

        # -----------------------------
        # Correct OTP
        # -----------------------------

        if totp.verify(
            otp,
            valid_window=1
        ):

            user.failed_otp_attempts = 0

            user.otp_locked_until = None

            db.session.commit()

            login_user(user)

            session.pop(
                "temp_user_id",
                None
            )

            log_security_event(
                user.email,
                "2FA Login Successful"
            )

            # Login Email
            send_email(

                user.email,

                "Login Successful",

                f"""
Hello {user.full_name},

You have successfully logged into your account using Two-Factor Authentication.

If this wasn't you, please secure your account immediately.

Regards,
Security Team
"""
            )

            flash(
                "Login Successful!",
                "success"
            )

            return redirect(
                url_for("dashboard.dashboard_page")
            )

        # -----------------------------
        # Wrong OTP
        # -----------------------------

        user.failed_otp_attempts += 1

        if user.failed_otp_attempts >= 5:

            user.otp_locked_until = (
                datetime.utcnow() + timedelta(minutes=15)
            )

            db.session.commit()

            log_security_event(
                user.email,
                "OTP Locked (Too Many Failed Attempts)"
            )

            flash(
                "Too many incorrect OTP attempts. Try again after 15 minutes.",
                "danger"
            )

        else:

            db.session.commit()

            remaining = 5 - user.failed_otp_attempts

            log_security_event(
                user.email,
                "2FA Login Failed"
            )

            flash(
                f"Incorrect OTP. {remaining} attempt(s) remaining.",
                "warning"
            )

    return render_template(
        "login_2fa.html"
    )

# =====================================================
# Forgot Password
# =====================================================

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        user = User.query.filter_by(
            email=email
        ).first()

        if user:

            token = secrets.token_urlsafe(32)

            reset_token = PasswordResetToken(

                user_id=user.id,

                token=token,

                expires_at=datetime.utcnow() + timedelta(minutes=15)

            )

            db.session.add(reset_token)

            db.session.commit()

            reset_link = url_for(

                "auth.reset_password",

                token=token,

                _external=True

            )

            send_reset_password_email(

                user.full_name,

                user.email,

                reset_link

            )

        flash(

            "If the email exists, a password reset link has been sent.",

            "info"

        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "forgot_password.html"
    )

# =====================================================
# Reset Password
# =====================================================

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    reset_token = PasswordResetToken.query.filter_by(

        token=token,

        is_used=False

    ).first()

    if not reset_token:

        flash(

            "Invalid password reset link.",

            "danger"

        )

        return redirect(
            url_for("auth.login")
        )

    if reset_token.expires_at < datetime.utcnow():

        flash(

            "Password reset link has expired.",

            "danger"

        )

        return redirect(
            url_for("auth.login")
        )

    user = User.query.get(
        reset_token.user_id
    )

    if request.method == "POST":

        password = request.form.get(
            "password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        if password != confirm_password:

            flash(

                "Passwords do not match.",

                "danger"

            )

            return redirect(request.url)

        user.password = bcrypt.generate_password_hash(

            password

        ).decode("utf-8")

        reset_token.is_used = True

        db.session.commit()

        log_security_event(

            user.email,

            "Password Reset"

        )

        send_password_changed_email(

            user.full_name,

            user.email

        )

        flash(

            "Password updated successfully. Please login.",

            "success"

        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "reset_password.html"
    )


# =====================================================
# Logout
# =====================================================

@auth.route("/logout")
@login_required
def logout():

    # Security Log
    log_security_event(
        current_user.email,
        "Logout"
    )

    # Optional Logout Email
    # Uncomment if you want email notification on logout.
    #
    # send_email(
    #     current_user.email,
    #     "Logout Successful",
    #     f"""
    # Hello {current_user.full_name},
    #
    # Your account has been logged out successfully.
    #
    # Regards,
    # Security Team
    # """
    # )

    logout_user()

    session.pop(
        "temp_user_id",
        None
    )

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )