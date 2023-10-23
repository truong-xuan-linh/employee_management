from flask import session as flask_session
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

from src.pccc.user import user
from src.pccc.admin import admin
from src.pccc.database import session, Account

#Global variable
TRAINING_TIME_DIR="./static/last_training.pkl"

# Init App
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # replace by real secret key
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(admin, url_prefix="/admin")

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
    return user

def decision(role):
    if role == "admin":
        return redirect(url_for('admin.dashboard'))
    elif role == "user":
        return redirect(url_for('user.qr_scan'))

@app.route('/', methods=["GET", "POST"])
def login():
    logout_user()
    if request.method == "POST":
        # Get user name, password from UI form
        username = request.form["username"]
        password = request.form["password"]
        
        #Get accout info from sql database
        db_account = session.query(Account).filter_by(MaNV=username).first()

        #Check valid or not
        if db_account and db_account.PassWord == password:
            user = User()
            user.id = username
            user.role = db_account.Role
            flask_session["bophan"] = db_account.BoPhan
            login_user(user)
            return decision(current_user.role)
        
        else:
            return render_template('login.html', error=True)
            
    return render_template('login.html')

if __name__ == "__main__":
    # app.run(host= '0.0.0.0', debug=True, ssl_context='adhoc')
    app.run(debug=True)
# app.run(debug=True)