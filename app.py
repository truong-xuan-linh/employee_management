from flask import session as flask_session
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from functools import wraps

from src.system.directional import directional

from src.pccc.user import user
from src.pccc.admin_v2 import admin
from src.pccc.database import session, Account, NhanVien

from src.attendance.user import attendance
from src.guard.user import guard
from src.on_leave.user import on_leave
# Global variable
TRAINING_TIME_DIR = "./static/last_training.pkl"

# Init App
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # replace by real secret key
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(attendance, url_prefix="/attendance")
app.register_blueprint(directional, url_prefix="/directional")
app.register_blueprint(guard, url_prefix="/guard")
app.register_blueprint(on_leave, url_prefix="/on-leave")

# Init Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# Class UserMixin help implement some related methods with users
class User(UserMixin):
    def __init__(self) -> None:
        super().__init__()
        self.role = None


# Load user session from flask storage
@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    print(user_id)
    staff_info = session.query(NhanVien).filter_by(MaNV=user_id).first()
    user.MaNV = staff_info.MaNV
    user.HoTen = staff_info.HoTen
    user.BoPhan = staff_info.BoPhan
    user.PhongBan = staff_info.PhongBan
    return user


def decision(roles):
    if "admin" in roles:
        flask_session["all_done"] = 0
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('directional.options'))


@app.route('/', methods=["GET", "POST"])
def login():
    logout_user()
    if request.method == "POST":
        # Get username, password from UI form
        username = request.form["username"]
        password = request.form["password"]

        # Get account info from sql database
        db_account = session.query(Account).filter_by(MaNV=username).first()

        # Check valid or not
        if db_account and db_account.PassWord == password:
            user = User()
            user.id = username
            user.role = [role.strip() for role in db_account.Role.split(",")]
            flask_session["bophan"] = db_account.BoPhan
            flask_session["phongban"] = db_account.PhongBan
            flask_session["role"] = user.role
            login_user(user)
            return decision(flask_session["role"])

        else:
            return render_template('system/login.html', error=True)

    return render_template('system/login.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')