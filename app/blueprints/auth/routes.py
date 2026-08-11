from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, AuditLog
from app import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active_account:
                flash('Your account has been deactivated. Contact System Administrator.', 'danger')
                return render_template('auth/login.html')
                
            login_user(user)
            user.last_login = datetime.utcnow()
            
            log = AuditLog(
                event_type='ADMIN_LOGIN' if user.is_admin() else 'STAFF_LOGIN',
                username=user.username,
                ip_address=request.remote_addr,
                details=f"User {user.username} logged in successfully."
            )
            db.session.add(log)
            db.session.commit()
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log = AuditLog(
        event_type='LOGOUT',
        username=current_user.username,
        ip_address=request.remote_addr,
        details=f"User {current_user.username} logged out."
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', '').strip()
        job_title = request.form.get('job_title', '').strip()
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('auth/register.html')
            
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            department=department,
            job_title=job_title,
            role='AUDITEE'
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')
