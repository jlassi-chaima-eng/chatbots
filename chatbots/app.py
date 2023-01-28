from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from socket import IPPROTO_FRAGMENT
from flask import Flask, render_template, request, jsonify,flash,redirect, url_for
from numpy import extract
from flask_login import UserMixin,login_user,login_manager, logout_user, login_required, current_user
from sqlalchemy.sql import func
from chat import get_response
import json
import os
import re 
# from app_bull import simple_page

basedir = os.path.abspath(os.path.dirname(__file__))
# from flaskext.mysql import MYSQL
from flask_sqlalchemy import SQLAlchemy 
# from m import User
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# from flask_mysqldb import Mysql
db=SQLAlchemy()
# os.path.join(basedir, {db_Name}
db_Name="database.db"
UPLOAD_FOLDER = 'static/images/'
app=Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:/// {db_Name}'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "helloworld"
db.init_app(app)
# app.register_blueprint(simple_page)
# pour la creation d'un bd

def create_database():
    if not os.path.exists("chatbots/"+db_Name):
        

        with app.app_context():
             db.create_all()
             print("created db!!")

class User (db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    pseudo=db.Column(db.String(150),unique=True)
    email=db.Column(db.String(150),unique=True)
    mdp=db.Column(db.String(150))
    genre=db.Column(db.String(150))
    date_created=db.Column(db.DateTime(timezone=True),default=func.now())
    roles=db.Column(db.String(150),default='user')
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    content=db.Column(db.Text, nullable=False)
    lieu=db.Column(db.Text, nullable=False)
    name=db.Column(db.Text, nullable=False)
    img=db.Column(db.Text, nullable=False)
    name1=db.Column(db.Text, nullable=False)
    video=db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref='post', passive_deletes=True)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)

create_database()
class MyModelView(ModelView):
      def is_accessible(self):
          return current_user.roles=='admin'

admin=Admin(app,name='Control Panel')
admin.add_view(MyModelView(User,db.session))
admin.add_view(MyModelView(Post,db.session))
admin.add_view(MyModelView(Comment,db.session))






login_manager= LoginManager()
login_manager.login_view="app.login"
login_manager.init_app(app)

#session
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# verification du compte 
@app.route("/",methods=['GET','POST'])
def  login():
    if request.method=='POST':
        email=request.form.get("email")
        mdp=request.form.get("mdp")
        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.mdp, mdp):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('index_get'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html",user=current_user)

# creation d'un utilisateur
@app.route("/signup",methods=['GET','POST'])
def  signUp():
    if request.method =='POST':
        name=request.form.get("pseudo")
        email=request.form.get("email")
        mdp1=request.form.get("mdp1")
        mdp2=request.form.get("mdp2")
        genre=request.form.get("genre")
        email_exists=User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(pseudo=name).first()
       
        if  email_exists :
            flash('Email is already in use ' ,category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif mdp1 != mdp2:
            flash('Password don\'t match!', category='error')
        elif len(name) < 2:
            flash('Username is too short.', category='error')
        elif len(mdp1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, pseudo=name, genre=genre,mdp=generate_password_hash(
                mdp1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('index_get'))

   
    return render_template("signup.html",user=current_user)

@app.route("/accueil")
def index_get():
    posts = Post.query.all()
    return render_template("ind.html",user=current_user,posts=posts)

@app.post("/predict")

def predict():
    text =request.get_json().get("message")
    response=get_response(text)
    message={"answer":response}
    return jsonify(message)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/creer_post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        content = request.form.get('content')
        lieu = request.form.get('lieu')
        pic=request.files['pic']
        if not pic :
            return 'no pic'
        filename = secure_filename(pic.filename)
        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        picVideo=request.files['picVideo']
        if not picVideo :
            return "no Video"
        filename1 = secure_filename(picVideo.filename)
        picVideo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        if not text:
            flash('Post cannot be empty', category='error')
        elif not content:
            flash('content cannot be empty', category='error')
        else:
            post = Post(text=text,content=content,lieu=lieu ,name=filename,img=pic.read(), name1=filename1,video=picVideo.read(),author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('index_get'))
    return render_template('CREE.html', user=current_user)
        
# @app.route("/test", methods=['GET', 'POST'])
# @login_required
# def test():
#     return render_template("single.html")

@app.route("/<id>", methods=['GET', 'POST'])
@login_required
def post_detail(id):
    post=Post.query.filter(Post.id==id).first()
    # return redirect(url_for('post_detail',user=current_user,post=post))
    return render_template("single.html",user=current_user,post=post)

@app.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('index_get'))
@app.route("/update_post/<p_id>", methods=['GET', 'POST'])
@login_required
def update_post(p_id):
   
    if request.method == "POST":
        update = Post.query.filter_by(id=p_id).first()
        text = request.form.get('text')
        content = request.form.get('content')
        pic=request.files['pic']
        if not pic :
            flash('no pic', category='error') 
        filename = secure_filename(pic.filename)
        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        picVideo=request.files['picVideo']
        if not picVideo :
           
            flash('no Video', category='error') 
        filename1 = secure_filename(picVideo.filename)
        picVideo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        if not text:
            flash('Post cannot be empty', category='error')      
        if not update:
            flash("Post does not exist.", category='error')
        if current_user.id != update.author:
            flash('You do not have permission to update this update.', category='error')
        else:
            update.text=text
            update.content=content
            update.name=filename
            update.img=pic.read()
            update.name1=filename1
            update.video=picVideo.read()
            update.author=current_user.id
            db.session.commit()
            flash('Post updated!', category='success')
            return redirect(url_for('index_get'))
    return render_template('update.html', user=current_user)


@app.route("/taccueil/2")
def taccueil():
    posts = Post.query.all()
    return render_template('update.html', user=current_user)

    # return render_template("taccueil.html",posts=posts)
# comment
@app.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment( text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
    
    return redirect(url_for('post_detail',id=post_id))
@app.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('post_detail',id=comment.post_id))
@app.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})
@app.route("/dashbord")
@login_required
def dashbord():
    # p_t= Post.query.all()
    post_like = db.session.query(db.func.count(Like.id),Post.text).join(Post).group_by(Like.post_id).all()

    p_l = []
    for pl, _ in post_like:
        p_l.append(pl)
    print(p_l)    
    p_t=[]
    i=1
    for pt  in post_like:
        print(pt)       
        for p in range(1,len(post_like)):
            print(pt[i])
            p_t.append(pt[i])
    print(p_t)
    return render_template('dashbord.html',post_like=json.dumps(p_l),p_t=json.dumps(p_t))
 
if __name__=="__main__":
    app.run(debug=True)