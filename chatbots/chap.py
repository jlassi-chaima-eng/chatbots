# from flask_login import UserMixin,login_user,login_manager, logout_user, login_required, current_user

from flask import Flask, render_template, request, jsonify,flash,redirect, url_for

app=Flask(__name__) 


@app.get("/login")
def index():
    return render_template("login.html")


@app.get("/blog")
def blog():
    return render_template("blog.html")

if __name__=="__main__":
    app.run(debug=True)
