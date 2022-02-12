from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, BuyItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/market", methods=["GET", "POST"])
@login_required
def market():
    buy_form = BuyItemForm()
    if request.method == "POST":
        buy_item = request.form.get("buy_item")
        b_item_object = Item.query.filter_by(name=buy_item).first()
        if b_item_object:
            if current_user.can_buy(b_item_object):
                b_item_object.buy(current_user)
                flash(
                    f"Congratulations! You buy {b_item_object} for ${b_item_object.price}", category='success'
                )
            else:
                flash(f"You dont have money for buy {b_item_object}", category="danger")

        return redirect(url_for('market'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        return render_template("market.html", items=items, buy_form=buy_form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(
            f"Account created. You are now logged in as {user_to_create.username}",
            category="success",
        )

        return redirect(url_for("market"))
    if form.errors != {}:  # если нет ошибок из валидации формы
        for err_msg in form.errors.values():
            flash(f"***Error***: {err_msg}", category="danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(
                f"Success. You are logged in as: {attempted_user.username}",
                category="success",
            )
            return redirect(url_for("market"))
        else:
            flash("Username and password are not match.", category="danger")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("home"))
