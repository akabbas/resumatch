"""
Authentication Blueprint for ResuMatch
Handles user login, registration, profile management, and authentication
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
try:
    from werkzeug.urls import url_parse
except ImportError:
    from urllib.parse import urlparse as url_parse
from forms import LoginForm, RegistrationForm, ProfileUpdateForm, PasswordResetRequestForm, PasswordResetForm
from auth_utils import create_user, authenticate_user, get_user_stats, upgrade_user_subscription
from models import db, User, Resume
import os

# Create authentication blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user, message = authenticate_user(form.email.data, form.password.data)
        
        if user:
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('auth.dashboard')
            return redirect(next_page)
        else:
            flash(message, 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user, message = create_user(
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        
        if user:
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management route"""
    form = ProfileUpdateForm()
    
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
    
    return render_template('auth/profile.html', title='Profile', form=form)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request route"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        # TODO: Implement password reset email functionality
        flash('Password reset functionality coming soon!', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', title='Reset Password', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    # TODO: Implement token validation
    form = PasswordResetForm()
    if form.validate_on_submit():
        # TODO: Implement password reset
        flash('Password reset functionality coming soon!', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    """Subscription upgrade route"""
    if current_user.subscription_tier != 'free':
        flash('You are already on a premium plan!', 'info')
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        plan = request.form.get('plan')
        if plan in ['pro', 'enterprise']:
            success, message = upgrade_user_subscription(current_user.id, plan)
            if success:
                flash(f'Successfully upgraded to {plan.title()} plan!', 'success')
                return redirect(url_for('auth.dashboard'))
            else:
                flash(message, 'error')
        else:
            flash('Invalid plan selected.', 'error')
    
    return render_template('auth/upgrade.html', title='Upgrade Plan')

@auth.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route"""
    # Get user statistics
    stats = get_user_stats(current_user.id)
    
    # Get user's resumes
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.updated_at.desc()).all()
    
    return render_template('dashboard.html', title='Dashboard', stats=stats, resumes=resumes)

@auth.route('/api/user-stats')
@login_required
def user_stats():
    """API endpoint for user statistics"""
    stats = get_user_stats(current_user.id)
    return jsonify(stats)

@auth.route('/api/upgrade-subscription', methods=['POST'])
@login_required
def api_upgrade_subscription():
    """API endpoint for subscription upgrade"""
    data = request.get_json()
    plan = data.get('plan')
    
    if not plan or plan not in ['pro', 'enterprise']:
        return jsonify({'success': False, 'message': 'Invalid plan'}), 400
    
    success, message = upgrade_user_subscription(current_user.id, plan)
    return jsonify({'success': success, 'message': message})

@auth.route('/api/delete-account', methods=['POST'])
@login_required
def delete_account():
    """API endpoint for account deletion"""
    # TODO: Implement account deletion with confirmation
    flash('Account deletion functionality coming soon!', 'info')
    return redirect(url_for('auth.profile'))
