from flask_login import login_required, current_user
from flask import render_template, Blueprint

directional = Blueprint("directional", __name__)

@directional.route("", methods=['GET', 'POST'])
@login_required
def options():
    return render_template("system/directional.html", name=current_user.HoTen)