from flask_mail import Message
from extensions import mail


# =====================================================
# Generic Email Function
# =====================================================

def send_email(recipient, subject, body):

    msg = Message(
        subject=subject,
        recipients=[recipient]
    )

    msg.body = body

    try:

        mail.send(msg)

        print(f"[EMAIL SENT] {recipient}")

    except Exception as e:

        print(f"[EMAIL ERROR] {e}")


# =====================================================
# Registration Email
# =====================================================

def send_registration_email(full_name, email):

    body = f"""
Hello {full_name},

Your account has been created successfully.

Welcome to the Secure Two-Factor Authentication System.

Regards,
Security Team
"""

    send_email(
        email,
        "Registration Successful",
        body
    )


# =====================================================
# Login Email
# =====================================================

def send_login_email(full_name, email):

    body = f"""
Hello {full_name},

A successful login to your account has been detected.

If this wasn't you, please change your password immediately.

Regards,
Security Team
"""

    send_email(
        email,
        "Login Successful",
        body
    )


# =====================================================
# Account Locked Email
# =====================================================

def send_account_locked_email(full_name, email):

    body = f"""
Hello {full_name},

Your account has been locked because of too many failed login attempts.

The account will automatically unlock after 15 minutes.

If this wasn't you, please reset your password immediately.

Regards,
Security Team
"""

    send_email(
        email,
        "Security Alert - Account Locked",
        body
    )


# =====================================================
# Password Reset Email
# =====================================================

def send_reset_password_email(full_name, email, reset_link):

    body = f"""
Hello {full_name},

A password reset request has been received.

Click the link below to reset your password:

{reset_link}

This link will expire in 15 minutes.

If you did not request this, please ignore this email.

Regards,
Security Team
"""

    send_email(
        email,
        "Reset Your Password",
        body
    )


# =====================================================
# Password Changed Email
# =====================================================

def send_password_changed_email(full_name, email):

    body = f"""
Hello {full_name},

Your password has been changed successfully.

If you did not perform this action, please contact the administrator immediately.

Regards,
Security Team
"""

    send_email(
        email,
        "Password Changed Successfully",
        body
    )


# =====================================================
# 2FA Enabled Email
# =====================================================

def send_2fa_enabled_email(full_name, email):

    body = f"""
Hello {full_name},

Two-Factor Authentication has been enabled on your account successfully.

Your account is now protected with Google Authenticator.

Regards,
Security Team
"""

    send_email(
        email,
        "2FA Enabled Successfully",
        body
    )


# =====================================================
# Logout Email (Optional)
# =====================================================

def send_logout_email(full_name, email):

    body = f"""
Hello {full_name},

Your account has been logged out successfully.

If this wasn't you, please secure your account immediately.

Regards,
Security Team
"""

    send_email(
        email,
        "Logout Successful",
        body
    )