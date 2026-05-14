from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app import db, bcrypt

from app.models import (
    User,
    Message,
    AuditLog
)

from app.forms import (
    RegistrationForm,
    LoginForm,
    EditProfileForm
)

from app.crypto.crypto_utils import (
    encrypt_message,
    decrypt_message
)

from app.utils.decorators import (
    admin_required
)

from app.audit.audit_utils import (
    log_action
)

from werkzeug.utils import (
    secure_filename
)

import os


main = Blueprint(
    'main',
    __name__
)


@main.route('/')
def home():

    return render_template(
        'index.html'
    )


@main.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:

        return redirect(
            url_for('main.dashboard')
        )

    form = RegistrationForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:

            flash(
                'Email already exists'
            )

            return redirect(
                url_for('main.register')
            )

        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode('utf-8')

        role = 'user'

        if form.email.data == 'admin@gmail.com':

            role = 'admin'

        user = User(

            username=form.username.data,

            email=form.email.data,

            password=hashed_password,

            role=role
        )

        db.session.add(user)

        db.session.commit()

        flash(
            'Account created successfully'
        )

        return redirect(
            url_for('main.login')
        )

    return render_template(
        'register.html',
        form=form
    )


@main.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for('main.dashboard')
        )

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            form.password.data
        ):

            login_user(user)

            log_action(
                user.id,
                'User logged in'
            )

            flash(
                'Login successful'
            )

            return redirect(
                url_for('main.dashboard')
            )

        flash(
            'Invalid email or password'
        )

    return render_template(
        'login.html',
        form=form
    )


@main.route('/dashboard')
@login_required
def dashboard():

    return render_template(
        'dashboard.html'
    )


@main.route('/logout')
@login_required
def logout():

    log_action(
        current_user.id,
        'User logged out'
    )

    logout_user()

    flash(
        'Logged out successfully'
    )

    return redirect(
        url_for('main.login')
    )


@main.route('/profile')
@login_required
def profile():

    return render_template(
        'profile.html'
    )


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = EditProfileForm()

    if form.validate_on_submit():

        current_user.username = form.username.data

        current_user.bio = form.bio.data

        if form.avatar.data:

            file = form.avatar.data

            filename = secure_filename(
                file.filename
            )

            upload_path = os.path.join(
                'app/static/uploads/avatars',
                filename
            )

            file.save(upload_path)

            current_user.avatar = filename

        db.session.commit()

        flash(
            'Profile updated successfully'
        )

        return redirect(
            url_for('main.profile')
        )

    form.username.data = current_user.username

    form.bio.data = current_user.bio

    return render_template(
        'edit_profile.html',
        form=form
    )


@main.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():

    users = User.query.filter(
        User.id != current_user.id
    ).all()

    selected_user_id = request.args.get(
        'user_id'
    )

    selected_user = None

    messages = []

    if selected_user_id:

        selected_user = User.query.get(
            int(selected_user_id)
        )

        if request.method == 'POST':

            content = request.form.get(
                'content'
            )

            encrypted_content = encrypt_message(
                content
            )

            message = Message(

                sender_id=current_user.id,

                receiver_id=selected_user.id,

                encrypted_content=encrypted_content
            )

            db.session.add(message)

            db.session.commit()

            log_action(
                current_user.id,
                'Encrypted message sent'
            )

            return redirect(
                url_for(
                    'main.inbox',
                    user_id=selected_user.id
                )
            )

        all_messages = Message.query.filter(

            (
                (Message.sender_id == current_user.id) &
                (Message.receiver_id == selected_user.id)
            ) |

            (
                (Message.sender_id == selected_user.id) &
                (Message.receiver_id == current_user.id)
            )

        ).order_by(
            Message.timestamp.asc()
        ).all()

        for msg in all_messages:

            messages.append({

                'sender_id': msg.sender_id,

                'content': decrypt_message(
                    msg.encrypted_content
                ),

                'timestamp': msg.timestamp
            })

    return render_template(
        'inbox.html',
        users=users,
        selected_user=selected_user,
        messages=messages
    )


@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():

    users = User.query.all()

    total_users = User.query.count()

    total_admins = User.query.filter_by(
        role='admin'
    ).count()

    total_regular_users = User.query.filter_by(
        role='user'
    ).count()

    return render_template(

        'admin_dashboard.html',

        users=users,

        total_users=total_users,

        total_admins=total_admins,

        total_regular_users=total_regular_users
    )


@main.route('/audit')
@login_required
@admin_required
def audit_logs():

    logs = AuditLog.query.order_by(
        AuditLog.timestamp.desc()
    ).all()

    return render_template(
        'audit.html',
        logs=logs
    )


@main.route('/delete-user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(
        user_id
    )

    if user.role == 'admin':

        flash(
            'Admin cannot be deleted'
        )

        return redirect(
            url_for('main.admin_dashboard')
        )

    AuditLog.query.filter_by(
        user_id=user.id
    ).delete()

    Message.query.filter(
        (
            Message.sender_id == user.id
        ) |
        (
            Message.receiver_id == user.id
        )
    ).delete()

    db.session.delete(user)

    db.session.commit()

    log_action(
        current_user.id,
        f'Admin deleted user {user.username}'
    )

    flash(
        'User deleted successfully'
    )

    return redirect(
        url_for('main.admin_dashboard')
    )