import os
import markdown
import bleach
from bleach.sanitizer import Cleaner
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from blog import app, db, bcrypt, login_manager, mde
from blog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

#Home Page
@app.route('/')
def home():
	page = request.args.get('page',1,type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=4)
	len_post = len(Post.query.all())

	return render_template('home.html',posts=posts,title='Home',len_post=len_post)

#Login Page
@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password','danger')

	return render_template('login.html',title='Login',form=form)

#Register Page
@app.route('/register',methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your Account has been created! You are now able to login','success')
		return redirect(url_for('login'))
	return render_template('register.html',title='Register',form=form)

#Function for Saving Profile Picture
def save_pictute(form_picture):

    renadom_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = renadom_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn	



#Account Page
@app.route('/account',methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:

			picture_file = save_pictute(form.picture.data)
			current_user.image_file = picture_file

		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!','success')
		return redirect(url_for('account'))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	image_file = url_for('static',filename='profile_pics/' + current_user.image_file)	 	
	return render_template('account.html',title='Account',image_file=image_file,form=form)


#New Post Page
@app.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():

		session['content'] = request.form['content']
		html = markdown.markdown(request.form['content'],extensions=['nl2br'],safe_mode=True,output_format='html5')
		# Tags deemed safe
		allowed_tags = [
		'a','abbr','acronym','b','blockquote','code',
		'em','i','li','ol','pre','strong','ul','img',
		'h1','h2','h3','p','br'
		]
		# Attributes deemed safe
		allowed_attrs = {
		'*':['class'],
		'a':['href','rel'],
		'img':['src','alt']
		}
		# Sanitize HTML
		html_sanitized = bleach.clean(
			bleach.linkify(html),
			tags=allowed_tags,
			attributes=allowed_attrs
			)
		post = Post(title=form.title.data,content=html_sanitized,author=current_user,category=form.category_name.data)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!','success')
		return redirect(url_for('home'))
	return render_template('newpost.html',title='New Post',form=form)


#Edit Post
@app.route('/post/<int:post_id>')
def editpost(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('editpost.html',title=post.title,post=post)

#Update Post
@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
def update_post(post_id):
	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403)

	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!','success')
		return redirect(url_for('editpost',post_id=post_id))

	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content

	return render_template('update_post.html',title='Update Post',form=form)		

#Delete Post
@app.route('/delete_post/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!','success')
	return redirect(url_for('home'))	

#Users Posts
@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page',1,type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=4)

	return render_template('user_posts.html',posts=posts,user=user)	

#Categories List
@app.route("/index/categories/<string:catgname>")
def category(catgname):
	total_catg_post = db.session.query(Post).filter(Post.category == catgname).count()
	page = request.args.get('page',1,type=int)
	posts = Post.query.filter_by(category=catgname).order_by(Post.date_posted.desc()).paginate(page=page,per_page=4)
	return render_template('category_list.html',title='Categories',catgname=catgname,total_catg_post=total_catg_post,posts=posts)
	
#Logout
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))	