from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from hello.models import User
from hello.extensions import db

auth = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("登录成功！", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("products.list"))
        else:
            flash("用户名或密码错误", "danger")

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("auth.login"))
