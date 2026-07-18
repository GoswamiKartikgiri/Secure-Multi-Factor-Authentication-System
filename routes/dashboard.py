from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db, bcrypt
from utils.security_logger import log_security_event

dashboard = Blueprint("dashboard", __name__)


# ==========================
# Dashboard
# ==========================

@dashboard.route("/dashboard")
@login_required
def dashboard_page():

    return render_template(
        "dashboard.html",
        user=current_user
    )


# ==========================
# My Profile
# ==========================

@dashboard.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html",
        user=current_user
    )


# ==========================
# Edit Profile
# ==========================

@dashboard.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        full_name = request.form.get("full_name").strip()

        if not full_name:

            flash(
                "Full Name cannot be empty.",
                "danger"
            )

            return redirect(
                url_for("dashboard.edit_profile")
            )

        current_user.full_name = full_name

        db.session.commit()

        log_security_event(
            current_user.email,
            "Profile Updated"
        )

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.profile")
        )

    return render_template(
        "edit_profile.html",
        user=current_user
    )


# ==========================
# Change Password
# ==========================

@dashboard.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get("current_password")

        new_password = request.form.get("new_password")

        confirm_password = request.form.get("confirm_password")

        if not bcrypt.check_password_hash(
                current_user.password,
                current_password):

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("dashboard.change_password")
            )

        if new_password != confirm_password:

            flash(
                "New passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("dashboard.change_password")
            )

        if len(new_password) < 8:

            flash(
                "Password must be at least 8 characters long.",
                "warning"
            )

            return redirect(
                url_for("dashboard.change_password")
            )

        current_user.password = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        db.session.commit()

        log_security_event(
            current_user.email,
            "Password Changed"
        )

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.profile")
        )

    return render_template(
        "change_password.html"
    )