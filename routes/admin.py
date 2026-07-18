import csv
from io import StringIO, BytesIO
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Response
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from extensions import db, bcrypt

from models import (
    Admin,
    User,
    SecurityLog,
    RecoveryCode
)

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =====================================================
# Admin Authentication Check
# =====================================================

def admin_required():

    return "admin_id" in session


# =====================================================
# Admin Login
# =====================================================

@admin.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        administrator = Admin.query.filter_by(
            email=email
        ).first()

        if administrator and bcrypt.check_password_hash(
            administrator.password,
            password
        ):

            session["admin_id"] = administrator.id

            session["admin_name"] = administrator.full_name

            flash(
                "Administrator Login Successful.",
                "success"
            )

            return redirect(
                url_for("admin.dashboard")
            )

        flash(
            "Invalid Administrator Credentials.",
            "danger"
        )

    return render_template(
        "admin/login.html"
    )


# =====================================================
# Dashboard
# =====================================================

@admin.route("/dashboard")
def dashboard():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    total_users = User.query.count()

    total_2fa = User.query.filter_by(
        is_2fa_enabled=True
    ).count()

    disabled_2fa = total_users - total_2fa

    locked_accounts = User.query.filter(
        User.account_locked_until != None
    ).count()

    active_accounts = total_users - locked_accounts

    total_logs = SecurityLog.query.count()

    successful_logins = SecurityLog.query.filter(
        SecurityLog.activity.like("%Successful%")
    ).count()

    failed_logins = SecurityLog.query.filter(
        SecurityLog.activity.like("%Failed%")
    ).count()

    recent_users = User.query.order_by(
        User.created_at.desc()
    ).limit(5).all()

    recent_logs = SecurityLog.query.order_by(
        SecurityLog.created_at.desc()
    ).limit(10).all()

    return render_template(

        "admin/dashboard.html",

        total_users=total_users,

        total_2fa=total_2fa,

        disabled_2fa=disabled_2fa,

        locked_accounts=locked_accounts,

        active_accounts=active_accounts,

        total_logs=total_logs,

        successful_logins=successful_logins,

        failed_logins=failed_logins,

        recent_users=recent_users,

        recent_logs=recent_logs

    )


# =====================================================
# Manage Users
# =====================================================

@admin.route("/users")
def users():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    search = request.args.get(
        "search",
        ""
    )

    if search:

        users = User.query.filter(

            (User.full_name.ilike(f"%{search}%")) |

            (User.email.ilike(f"%{search}%"))

        ).order_by(

            User.created_at.desc()

        ).all()

    else:

        users = User.query.order_by(

            User.created_at.desc()

        ).all()

    return render_template(

        "admin/users.html",

        users=users,

        search=search

    )


# =====================================================
# Security Logs
# =====================================================

@admin.route("/logs")
def logs():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    logs = SecurityLog.query.order_by(
        SecurityLog.created_at.desc()
    ).all()

    return render_template(

        "admin/logs.html",

        logs=logs

    )

# =====================================================
# Analytics
# =====================================================

@admin.route("/analytics")
def analytics():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    total_users = User.query.count()

    total_2fa = User.query.filter_by(
        is_2fa_enabled=True
    ).count()

    disabled_2fa = total_users - total_2fa

    locked_accounts = User.query.filter(
        User.account_locked_until != None
    ).count()

    active_accounts = total_users - locked_accounts

    successful_logins = SecurityLog.query.filter(
        SecurityLog.activity.like("%Successful%")
    ).count()

    failed_logins = SecurityLog.query.filter(
        SecurityLog.activity.like("%Failed%")
    ).count()

    return render_template(

        "admin/analytics.html",

        total_users=total_users,

        total_2fa=total_2fa,

        disabled_2fa=disabled_2fa,

        locked_accounts=locked_accounts,

        active_accounts=active_accounts,

        successful_logins=successful_logins,

        failed_logins=failed_logins

    )


# =====================================================
# User Details
# =====================================================

@admin.route("/user/<int:user_id>")
def user_details(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    logs = SecurityLog.query.filter_by(
        user_email=user.email
    ).order_by(
        SecurityLog.created_at.desc()
    ).limit(20).all()

    return render_template(

        "admin/user_details.html",

        user=user,

        logs=logs

    )


# =====================================================
# Unlock User
# =====================================================

@admin.route("/unlock-user/<int:user_id>")
def unlock_user(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    user.failed_login_attempts = 0

    user.failed_otp_attempts = 0

    user.account_locked_until = None

    user.otp_locked_until = None

    db.session.commit()

    flash(
        "User unlocked successfully.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# =====================================================
# Lock User
# =====================================================

@admin.route("/lock-user/<int:user_id>")
def lock_user(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    user.account_locked_until = datetime.utcnow() + timedelta(days=365)

    db.session.commit()

    flash(
        "User locked successfully.",
        "warning"
    )

    return redirect(
        url_for("admin.users")
    )


# =====================================================
# Enable 2FA
# =====================================================

@admin.route("/enable-2fa/<int:user_id>")
def enable_2fa(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    user.is_2fa_enabled = True

    db.session.commit()

    flash(
        "2FA Enabled.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# =====================================================
# Disable 2FA
# =====================================================

@admin.route("/disable-2fa/<int:user_id>")
def disable_2fa(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    user.is_2fa_enabled = False

    db.session.commit()

    flash(
        "2FA Disabled.",
        "warning"
    )

    return redirect(
        url_for("admin.users")
    )


# =====================================================
# Delete User
# =====================================================

@admin.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    SecurityLog.query.filter_by(
        user_email=user.email
    ).delete()

    RecoveryCode.query.filter_by(
        user_id=user.id
    ).delete()

    db.session.delete(user)

    db.session.commit()

    flash(
        "User deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )

# =====================================================
# Export Users (CSV)
# =====================================================

@admin.route("/export/users")
def export_users():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Full Name",
        "Email",
        "2FA Enabled",
        "Failed Login Attempts",
        "OTP Failed Attempts",
        "Account Locked",
        "Registered On"
    ])

    users = User.query.order_by(
        User.id
    ).all()

    for user in users:

        writer.writerow([
            user.id,
            user.full_name,
            user.email,
            "Enabled" if user.is_2fa_enabled else "Disabled",
            user.failed_login_attempts,
            user.failed_otp_attempts,
            "Yes" if user.account_locked_until else "No",
            user.created_at
        ])

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={
            "Content-Disposition":
            "attachment; filename=users_report.csv"
        }

    )


# =====================================================
# Export Security Logs (CSV)
# =====================================================

@admin.route("/export/logs")
def export_logs():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "User Email",
        "Activity",
        "IP Address",
        "Date & Time"
    ])

    logs = SecurityLog.query.order_by(
        SecurityLog.id
    ).all()

    for log in logs:

        writer.writerow([
            log.id,
            log.user_email,
            log.activity,
            log.ip_address,
            log.created_at
        ])

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={
            "Content-Disposition":
            "attachment; filename=security_logs.csv"
        }

    )


# =====================================================
# Export Users PDF
# =====================================================

@admin.route("/export/users/pdf")
def export_users_pdf():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(buffer)

    elements = []

    styles = getSampleStyleSheet()

    elements.append(

        Paragraph(

            "Users Report",

            styles["Heading1"]

        )

    )

    data = [[

        "ID",

        "Name",

        "Email",

        "2FA"

    ]]

    users = User.query.order_by(
        User.id
    ).all()

    for user in users:

        data.append([

            str(user.id),

            user.full_name,

            user.email,

            "Enabled"
            if user.is_2fa_enabled
            else
            "Disabled"

        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.grey),

        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    elements.append(table)

    document.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return Response(

        pdf,

        mimetype="application/pdf",

        headers={
            "Content-Disposition":
            "attachment; filename=users_report.pdf"
        }

    )

# =====================================================
# Export Security Logs PDF
# =====================================================

@admin.route("/export/logs/pdf")
def export_logs_pdf():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(buffer)

    elements = []

    styles = getSampleStyleSheet()

    elements.append(

        Paragraph(

            "Security Logs Report",

            styles["Heading1"]

        )

    )

    data = [[

        "User",

        "Activity",

        "IP Address",

        "Date"

    ]]

    logs = SecurityLog.query.order_by(
        SecurityLog.id
    ).all()

    for log in logs:

        data.append([

            log.user_email,

            log.activity,

            log.ip_address,

            str(log.created_at)

        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    elements.append(table)

    document.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return Response(

        pdf,

        mimetype="application/pdf",

        headers={

            "Content-Disposition":

            "attachment; filename=security_logs.pdf"

        }

    )


# =====================================================
# Reset User Password
# =====================================================

@admin.route("/reset-password/<int:user_id>", methods=["GET", "POST"])
def reset_user_password(user_id):

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        password = request.form.get("password")

        confirm = request.form.get("confirm_password")

        if password != confirm:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(request.url)

        user.password = bcrypt.generate_password_hash(

            password

        ).decode("utf-8")

        db.session.commit()

        flash(

            "Password reset successfully.",

            "success"

        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(

        "admin/reset_user_password.html",

        user=user

    )


# =====================================================
# Settings
# =====================================================

@admin.route("/settings")
def settings():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    return render_template(
        "admin/settings.html"
    )


# =====================================================
# Admin Profile
# =====================================================

@admin.route("/profile")
def profile():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    administrator = Admin.query.get(
        session["admin_id"]
    )

    return render_template(

        "admin/profile.html",

        admin=administrator

    )


# =====================================================
# Change Admin Password
# =====================================================

@admin.route("/change-password", methods=["GET", "POST"])
def change_password():

    if not admin_required():

        return redirect(
            url_for("admin.login")
        )

    administrator = Admin.query.get(
        session["admin_id"]
    )

    if request.method == "POST":

        current_password = request.form.get(
            "current_password"
        )

        new_password = request.form.get(
            "new_password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        if not bcrypt.check_password_hash(

            administrator.password,

            current_password

        ):

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(request.url)

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(request.url)

        administrator.password = bcrypt.generate_password_hash(

            new_password

        ).decode("utf-8")

        db.session.commit()

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    return render_template(
        "admin/change_password.html"
    )


# =====================================================
# Admin Logout
# =====================================================

@admin.route("/logout")
def logout():

    session.clear()

    flash(

        "Administrator Logged Out Successfully.",

        "success"

    )

    return redirect(
        url_for("admin.login")
    )