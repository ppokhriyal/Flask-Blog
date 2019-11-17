from flask_wtf import FlaskForm
from flask_mde import Mde, MdeField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from blog.models import User, Post


class RegistrationForm(FlaskForm):

    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a diffrent one.')
    def validate_email(self,email):

        user = User.query.filter_by(email=email.data).first()
        if user:
           raise ValidationError('That email is taken. Please choose a diffrent one.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Login')                        


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpeg','png'])])
    submit = SubmitField('Update')    

class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = MdeField('Content',validators=[InputRequired("Input Required"),Length(min=15,max=30000)])
    category_name = SelectField('Category Tag',choices=[('General','General'),('Citrix','Citrix'),('Vmware','Vmware Horizon'),('Linux','Linux'),('Bash','Bash'),('QT','QT'),('C++','C++'),('RDP','RDP'),
        ('PHP','PHP'),('Ubuntu','Ubuntu'),('Firefox','Firefox'),('Digital Signage','Digital Signage'),('Kernel','Kernel')])
    submit = SubmitField('Post')
    cancel = SubmitField('Cancel')
