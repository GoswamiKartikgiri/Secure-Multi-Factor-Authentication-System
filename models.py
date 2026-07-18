from datetime import datetime

from flask_login import UserMixin

from extensions import db


# =====================================================
# User Model
# =====================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
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

    # Google Authenticator Secret Key
    totp_secret = db.Column(
        db.String(100)
    )

    # 2FA Status
    is_2fa_enabled = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Login Security
    failed_login_attempts = db.Column(
        db.Integer,
        default=0
    )

    account_locked_until = db.Column(
        db.DateTime
    )

    # OTP Security
    failed_otp_attempts = db.Column(
        db.Integer,
        default=0
    )

    otp_locked_until = db.Column(
        db.DateTime
    )


# =====================================================
# Security Logs
# =====================================================

class SecurityLog(db.Model):

    __tablename__ = "security_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_email = db.Column(
        db.String(120)
    )

    activity = db.Column(
        db.String(200)
    )

    ip_address = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =====================================================
# Recovery Codes
# =====================================================

class RecoveryCode(db.Model):

    __tablename__ = "recovery_codes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    recovery_code = db.Column(
        db.String(30),
        unique=True
    )

    is_used = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =====================================================
# Admin
# =====================================================

class Admin(db.Model):

    __tablename__ = "admins"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
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

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =====================================================
# Password Reset Tokens
# =====================================================

class PasswordResetToken(db.Model):

    __tablename__ = "password_reset_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    token = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    is_used = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )