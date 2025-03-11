from app import db
from flask_login import UserMixin
from datetime import datetime, time, date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    health_tips = db.relationship('HealthTip', backref='user', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('HealthRecommendation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer)
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    health_goals = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Profile for User {self.user_id}>'

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # Scale of 1-10
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<MoodEntry {self.id} for User {self.user_id}>'

class HealthTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<HealthTip {self.id} for User {self.user_id}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Scale of 1-5
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<Feedback {self.id} from User {self.user_id}>'

class HealthRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(64), nullable=False)  # e.g., 'nutrition', 'exercise', 'sleep', 'mental_health'
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, default=1)  # 1-5, with 5 being highest priority
    date_created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<HealthRecommendation {self.id} ({self.category}) for User {self.user_id}>'


