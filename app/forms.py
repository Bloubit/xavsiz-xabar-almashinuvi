from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo
)

from flask_wtf.file import (
    FileField,
    FileAllowed
)


class RegistrationForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo(
                'password',
                message='Passwords must match'
            )
        ]
    )

    submit = SubmitField(
        'Register'
    )


class LoginForm(FlaskForm):

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        'Login'
    )


class EditProfileForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    bio = TextAreaField(
        'Bio'
    )

    avatar = FileField(
        'Profile Image',
        validators=[
            FileAllowed(
                ['jpg', 'png', 'jpeg'],
                'Images only'
            )
        ]
    )

    submit = SubmitField(
        'Save Changes'
    )