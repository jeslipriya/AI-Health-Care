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
    medications = db.relationship('Medication', backref='user', lazy=True, cascade='all, delete-orphan')
    medication_reminders = db.relationship('MedicationReminder', backref='user', lazy=True, cascade='all, delete-orphan')
    
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

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    instructions = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date)  # Can be null for medications taken indefinitely
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    reminders = db.relationship('MedicationReminder', backref='medication', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('MedicationLog', backref='medication', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medication {self.id} ({self.name}) for User {self.user_id}>'

class MedicationReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    days = db.Column(db.String(50), nullable=False, default="0,1,2,3,4,5,6")  # Stored as comma-separated days (e.g. "1,2,3,4,5" for weekdays)
    active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<MedicationReminder {self.id} for Medication {self.medication_id}>'
    
    def get_days_list(self):
        """Convert the days string to a list of integers"""
        if not self.days:
            return []
        return [int(day) for day in self.days.split(',')]
    
    def set_days_list(self, days_list):
        """Convert a list of day integers to a comma-separated string"""
        self.days = ','.join(str(day) for day in days_list)
    
    def get_formatted_time(self):
        """Return the time in a human-readable format"""
        if self.time:
            return self.time.strftime("%I:%M %p")
        return "No time set"
    
    def get_days_display(self):
        """Return a human-readable display of days"""
        days_map = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 
            4: "Friday", 5: "Saturday", 6: "Sunday"
        }
        days_list = self.get_days_list()
        
        if len(days_list) == 7:
            return "Every day"
        elif sorted(days_list) == [0, 1, 2, 3, 4]:
            return "Weekdays"
        elif sorted(days_list) == [5, 6]:
            return "Weekends"
        else:
            return ", ".join(days_map[day] for day in days_list)

class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    reminder_id = db.Column(db.Integer, db.ForeignKey('medication_reminder.id'), nullable=True)
    taken_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='taken')  # 'taken', 'skipped', 'missed'
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<MedicationLog {self.id} for Medication {self.medication_id} status: {self.status}>'
