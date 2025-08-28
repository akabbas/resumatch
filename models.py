"""
Database Models for ResuMatch User Account System
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    subscription_tier = db.Column(db.String(50), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to resumes
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email.split('@')[0]
    
    def can_create_resume(self):
        """Check if user can create a new resume based on subscription"""
        if self.subscription_tier == 'free':
            return len(self.resumes) < 3  # Free users get 3 resumes
        elif self.subscription_tier == 'pro':
            return len(self.resumes) < 50  # Pro users get 50 resumes
        else:  # enterprise
            return True  # Unlimited
    
    def get_usage_stats(self):
        """Get user's usage statistics"""
        total_resumes = len(self.resumes)
        this_month = len([r for r in self.resumes if r.created_at.month == datetime.utcnow().month])
        
        return {
            'total_resumes': total_resumes,
            'this_month': this_month,
            'subscription_tier': self.subscription_tier,
            'can_create_more': self.can_create_resume()
        }

class Resume(db.Model):
    """Resume data model"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    resume_data = db.Column(db.JSON, nullable=False)  # Store the full resume JSON
    job_description = db.Column(db.Text)
    job_title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    generated_pdf_url = db.Column(db.String(500))
    pdf_filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_template = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Resume {self.title} by User {self.user_id}>'
    
    def get_resume_data(self):
        """Get resume data as dictionary"""
        if isinstance(self.resume_data, str):
            return json.loads(self.resume_data)
        return self.resume_data
    
    def update_resume_data(self, new_data):
        """Update resume data and timestamp"""
        self.resume_data = new_data
        self.updated_at = datetime.utcnow()
    
    def get_summary(self):
        """Get a brief summary of the resume"""
        data = self.get_resume_data()
        summary = data.get('summary', '')
        if len(summary) > 100:
            return summary[:100] + '...'
        return summary

class UsageLog(db.Model):
    """Usage tracking for analytics"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'create_resume', 'download_pdf', etc.
    details = db.Column(db.JSON)  # Additional action details
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref='usage_logs')
    
    def __repr__(self):
        return f'<UsageLog {self.action} by User {self.user_id}>'

class Subscription(db.Model):
    """Subscription management"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tier = db.Column(db.String(50), nullable=False)  # 'free', 'pro', 'enterprise'
    status = db.Column(db.String(50), default='active')  # 'active', 'cancelled', 'expired'
    stripe_subscription_id = db.Column(db.String(255))  # Stripe subscription ID
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref='subscriptions')
    
    def __repr__(self):
        return f'<Subscription {self.tier} for User {self.user_id}>'
    
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        if self.current_period_end and datetime.utcnow() > self.current_period_end:
            return False
        return True


