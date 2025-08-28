"""
Authentication utilities for ResuMatch
"""

import bcrypt
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, current_user
from models import db, User, UsageLog
from flask import request

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(password, hashed):
    """Check if a password matches its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(email, password, first_name=None, last_name=None):
    """Create a new user account"""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email=email.lower()).first()
        if existing_user:
            return None, "User already exists"
        
        # Create new user
        user = User(
            email=email.lower(),
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            subscription_tier='free'
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log the action
        log_user_action(user.id, 'account_created')
        
        return user, "User created successfully"
    
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating user: {str(e)}"

def authenticate_user(email, password):
    """Authenticate a user with email and password"""
    try:
        user = User.query.filter_by(email=email.lower()).first()
        
        if user and check_password(password, user.password_hash):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log the action
            log_user_action(user.id, 'login_successful')
            
            return user, "Authentication successful"
        else:
            return None, "Invalid email or password"
    
    except Exception as e:
        return None, f"Authentication error: {str(e)}"

def log_user_action(user_id, action, details=None):
    """Log user actions for analytics"""
    try:
        log = UsageLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Don't fail if logging fails
        print(f"Failed to log user action: {e}")

def get_user_stats(user_id):
    """Get comprehensive user statistics"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        stats = user.get_usage_stats()
        
        # Add additional stats
        recent_resumes = [r for r in user.resumes if r.created_at > datetime.utcnow() - timedelta(days=30)]
        stats['recent_resumes'] = len(recent_resumes)
        stats['total_storage_mb'] = sum(len(str(r.resume_data)) / (1024 * 1024) for r in user.resumes)
        
        return stats
    
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return None

def can_user_access_feature(user_id, feature):
    """Check if user can access a specific feature based on subscription"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        feature_access = {
            'unlimited_resumes': user.subscription_tier in ['pro', 'enterprise'],
            'advanced_templates': user.subscription_tier in ['pro', 'enterprise'],
            'ai_optimization': user.subscription_tier in ['pro', 'enterprise'],
            'priority_support': user.subscription_tier == 'enterprise',
            'team_collaboration': user.subscription_tier == 'enterprise'
        }
        
        return feature_access.get(feature, False)
    
    except Exception as e:
        print(f"Error checking feature access: {e}")
        return False

def upgrade_user_subscription(user_id, new_tier):
    """Upgrade user's subscription tier"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        old_tier = user.subscription_tier
        user.subscription_tier = new_tier
        
        db.session.commit()
        
        # Log the upgrade
        log_user_action(user_id, 'subscription_upgraded', {
            'old_tier': old_tier,
            'new_tier': new_tier
        })
        
        return True, f"Subscription upgraded to {new_tier}"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error upgrading subscription: {str(e)}"

def delete_user_account(user_id):
    """Delete a user account and all associated data"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Log the deletion
        log_user_action(user_id, 'account_deleted')
        
        # Delete user (cascade will handle resumes and logs)
        db.session.delete(user)
        db.session.commit()
        
        return True, "Account deleted successfully"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting account: {str(e)}"


