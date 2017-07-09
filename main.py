from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re
import models

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'dillybar'


@app.before_request
def require_login():
    '''Restrict and redirect user to signup or login if trying to post without being logged in.'''

    allowed_routes = ['signup', 'login', 'blogpage', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    '''Displays the home page. Receives post from newpost form and redirects to blog page if requirements are met'''
    
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['body']
        blog_owner = request.form['username'] #TODO or is this ID? form needs work

        # validate that a user entered a title or body, flash errors if not valid
        if not blog_body or not blog_title:
            if not blog_title:
                flash('Please enter a title', 'error')
            if not blog_body:
                flash('Please enter content for your post', 'error')
            return render_template('newpost.html', title="New Blog Post")

        new_post = models.Blog(blog_title, blog_body, blog_owner)
        db.session.add(new_post)
        db.session.commit()
        return render_template('blogpage.html', post=new_post)

    return render_template('index.html', title='Blog Home Page')


@app.route('/login', methods=['POST', 'GET'])
def login():
    '''Display login page, if user successfully logs in store their username in the session
    and redirect to /newpost. If unsuccessful login flash error and reload login page'''

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = models.User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')

        if not user:
            flash('username does not exist', 'error')
        else:
            flash('User password incorrect', 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''Display signup page. If user enters valid username and password store the username
    in the session and redirect to the /newpost page.'''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = models.User.query.filter_by(username=username).first()

        if models.validate_user(username, password, verify):
            return render_template('signup.html', user_name=username)

        if not existing_user:
            new_user = models.User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    '''delete username from the session and redirect to the homepage'''
    del session['username']
    return redirect('/blog')


@app.route('/newpost')
def add_post():
    '''Display the new post template'''

    return render_template('newpost.html')

@app.route('/blog')
def blog_listings():
    '''Display all blogs in the database, or just a specific post if an ID is passed in the GET'''

    posts = models.Blog.query.order_by(models.Blog.pub_date.desc()).all()

    if request.args.get('id'):
        post_id = request.args.get('id')
        post = models.Blog.query.filter_by(id=post_id).first()
        return render_template('blogpage.html', post=post)

    return render_template('blog.html', posts=posts)


if __name__ == '__main__':
    app.run()