from flask import Flask, render_template

from config import Config

from extensions import (
    db,
    bcrypt,
    login_manager,
    mail
)

from models import User

from routes import (
    auth,
    dashboard,
    twofa,
    admin
)


# =====================================================
# Flask Application
# =====================================================

app = Flask(__name__)


# =====================================================
# Load Configuration
# =====================================================

app.config.from_object(Config)


# =====================================================
# Initialize Extensions
# =====================================================

db.init_app(app)

bcrypt.init_app(app)

login_manager.init_app(app)

mail.init_app(app)


# =====================================================
# Flask Login Configuration
# =====================================================

login_manager.login_view = "auth.login"

login_manager.login_message = "Please login to continue."

login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# =====================================================
# Register Blueprints
# =====================================================

app.register_blueprint(auth)

app.register_blueprint(dashboard)

app.register_blueprint(twofa)

app.register_blueprint(admin)


# =====================================================
# Home Page
# =====================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =====================================================
# Error Pages
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# =====================================================
# Create Database Tables
# =====================================================

with app.app_context():

    db.create_all()


# =====================================================
# Run Application
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False
    )