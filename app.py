import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import gemini_ai  # Import our Gemini AI integration instead of OpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///health_assistant.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after initializing db to avoid circular imports
from models import User, MoodEntry, HealthTip, UserProfile, Feedback, HealthRecommendation

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent mood entries
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).limit(7).all()
    
    # Get personalized health tips
    health_tips = HealthTip.query.filter_by(user_id=current_user.id).order_by(HealthTip.date.desc()).limit(3).all()
    
    # If no health tips exist, create a default one
    if not health_tips:
        default_tip = HealthTip(
            user_id=current_user.id,
            content="Stay hydrated by drinking at least 8 glasses of water daily.",
            date=datetime.now()
        )
        db.session.add(default_tip)
        db.session.commit()
        health_tips = [default_tip]
    
    return render_template('dashboard.html', mood_entries=mood_entries, health_tips=health_tips)

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/ask_chatbot', methods=['POST'])
@login_required
def ask_chatbot():
    user_input = request.json.get('message', '')
    
    try:
        # Use Gemini AI for health-related responses
        bot_response = gemini_ai.health_conversation(user_input)
        return jsonify({"response": bot_response})
    except Exception as e:
        logging.error(f"Gemini AI error: {str(e)}")
        return jsonify({"response": "I'm sorry, I'm having trouble connecting to my knowledge base. Please try again later."})

@app.route('/moodtracker')
@login_required
def moodtracker():
    # Get past mood entries
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).all()
    return render_template('moodtracker.html', mood_entries=mood_entries)

@app.route('/add_mood', methods=['POST'])
@login_required
def add_mood():
    mood_score = int(request.form.get('mood_score'))
    notes = request.form.get('notes', '')
    
    # Validate mood score
    if mood_score < 1 or mood_score > 10:
        flash('Mood score must be between 1 and 10', 'danger')
        return redirect(url_for('moodtracker'))
    
    # Create new mood entry
    new_entry = MoodEntry(
        user_id=current_user.id,
        mood_score=mood_score,
        notes=notes,
        date=datetime.now()
    )
    
    db.session.add(new_entry)
    db.session.commit()
    
    flash('Mood entry added successfully!', 'success')
    return redirect(url_for('moodtracker'))

@app.route('/healthtips')
@login_required
def healthtips():
    # Get user's health tips
    health_tips = HealthTip.query.filter_by(user_id=current_user.id).order_by(HealthTip.date.desc()).all()
    
    # Generate a new health tip if requested
    generate_new = request.args.get('generate', False)
    if generate_new or not health_tips:
        try:
            # Get user profile information for context
            profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            
            # Create user profile dictionary if profile exists
            user_profile = None
            if profile:
                user_profile = {
                    'age': profile.age,
                    'height': profile.height,
                    'weight': profile.weight,
                    'health_goals': profile.health_goals
                }
            
            # Generate health tip using Gemini AI
            new_tip_content = gemini_ai.generate_health_tip(user_profile)
            
            # Save the new tip
            new_tip = HealthTip(
                user_id=current_user.id,
                content=new_tip_content,
                date=datetime.now()
            )
            db.session.add(new_tip)
            db.session.commit()
            
            # Refresh the tips list
            health_tips = HealthTip.query.filter_by(user_id=current_user.id).order_by(HealthTip.date.desc()).all()
            
            flash('New health tip generated!', 'success')
        except Exception as e:
            logging.error(f"Error generating health tip: {str(e)}")
            flash('Unable to generate a new health tip at this time.', 'danger')
    
    return render_template('healthtips.html', health_tips=health_tips)

@app.route('/location')
@login_required
def location():
    return render_template('location.html')

@app.route('/dietandexercise')
@login_required
def dietandexercise():
    # Get user profile for personalized recommendations
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    diet_plan = ""
    exercise_plan = ""
    
    if profile:
        try:
            # Create user profile dictionary
            user_profile = {
                'age': profile.age,
                'height': profile.height,
                'weight': profile.weight,
                'health_goals': profile.health_goals
            }
            
            # Generate diet and exercise recommendations using Gemini AI
            recommendations = gemini_ai.generate_diet_exercise_plan(user_profile)
            
            # Extract plans from response
            diet_plan = recommendations.get('diet_plan', "Unable to generate diet recommendations at this time.")
            exercise_plan = recommendations.get('exercise_plan', "Unable to generate exercise recommendations at this time.")
            
        except Exception as e:
            logging.error(f"Error generating recommendations: {str(e)}")
            diet_plan = "Unable to generate diet recommendations at this time."
            exercise_plan = "Unable to generate exercise recommendations at this time."
    else:
        diet_plan = "Please complete your profile to receive personalized diet recommendations."
        exercise_plan = "Please complete your profile to receive personalized exercise recommendations."
    
    return render_template('dietandexercise.html', diet_plan=diet_plan, exercise_plan=exercise_plan)

@app.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    # Check if recommendations should be regenerated
    regenerate = request.args.get('regenerate', False)
    
    # Get user profile for personalized recommendations
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    user_has_profile = profile is not None
    
    # Get existing recommendations
    user_recommendations = HealthRecommendation.query.filter_by(user_id=current_user.id).order_by(
        HealthRecommendation.priority.desc(), 
        HealthRecommendation.date_created.desc()
    ).all()
    
    # If we need to regenerate or don't have any recommendations yet
    if regenerate or not user_recommendations:
        if profile:
            try:
                # Create user profile dictionary
                user_profile = {
                    'age': profile.age,
                    'height': profile.height,
                    'weight': profile.weight,
                    'health_goals': profile.health_goals
                }
                
                # Get recent mood entries for context
                recent_mood_entries = []
                mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(
                    MoodEntry.date.desc()
                ).limit(5).all()
                
                for entry in mood_entries:
                    recent_mood_entries.append({
                        'mood_score': entry.mood_score,
                        'notes': entry.notes,
                        'date': entry.date.strftime('%Y-%m-%d')
                    })
                
                # Generate new recommendations
                new_recommendations = gemini_ai.generate_health_recommendations(
                    user_profile, recent_mood_entries
                )
                
                # Clear existing recommendations if regenerating
                if regenerate:
                    HealthRecommendation.query.filter_by(user_id=current_user.id).delete()
                    db.session.commit()
                
                # Save new recommendations
                for rec in new_recommendations:
                    new_rec = HealthRecommendation(
                        user_id=current_user.id,
                        category=rec.get('category', 'general'),
                        title=rec.get('title', 'Health Recommendation'),
                        content=rec.get('content', 'No content provided'),
                        priority=min(5, max(1, int(rec.get('priority', 1)))),  # Ensure priority is 1-5
                        date_created=datetime.now(),
                        date_updated=datetime.now()
                    )
                    db.session.add(new_rec)
                
                db.session.commit()
                
                # Refresh the recommendations
                user_recommendations = HealthRecommendation.query.filter_by(user_id=current_user.id).order_by(
                    HealthRecommendation.priority.desc(), 
                    HealthRecommendation.date_created.desc()
                ).all()
                
                flash('Your personalized health recommendations have been updated!', 'success')
            except Exception as e:
                logging.error(f"Error generating recommendations: {str(e)}")
                flash('Unable to generate recommendations at this time. Please try again later.', 'danger')
        else:
            # If user doesn't have a profile, create a recommendation to complete it
            if not user_recommendations:
                profile_rec = HealthRecommendation(
                    user_id=current_user.id,
                    category='profile',
                    title='Complete Your Profile',
                    content='To receive personalized health recommendations, please complete your profile with your age, height, weight, and health goals.',
                    priority=5,
                    date_created=datetime.now(),
                    date_updated=datetime.now()
                )
                db.session.add(profile_rec)
                db.session.commit()
                
                user_recommendations = [profile_rec]
                flash('Please complete your profile to get personalized recommendations.', 'info')
    
    # Group recommendations by category for display
    recommendations_by_category = {}
    for rec in user_recommendations:
        if rec.category not in recommendations_by_category:
            recommendations_by_category[rec.category] = []
        recommendations_by_category[rec.category].append(rec)
    
    return render_template('recommendations.html', 
                          recommendations=user_recommendations,
                          recommendations_by_category=recommendations_by_category,
                          user_has_profile=user_has_profile)

@app.route('/firstaid')
def firstaid():
    return render_template('firstaid.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update or create user profile
        if not user_profile:
            user_profile = UserProfile(user_id=current_user.id)
        
        user_profile.age = request.form.get('age')
        user_profile.height = request.form.get('height')
        user_profile.weight = request.form.get('weight')
        user_profile.health_goals = request.form.get('health_goals')
        
        db.session.add(user_profile)
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', profile=user_profile)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        content = request.form.get('content')
        rating = int(request.form.get('rating'))
        
        # Validate rating
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5', 'danger')
            return redirect(url_for('feedback'))
        
        # Create new feedback
        new_feedback = Feedback(
            user_id=current_user.id,
            content=content,
            rating=rating,
            date=datetime.now()
        )
        
        # Analyze sentiment using Gemini AI if content is provided
        if content:
            try:
                sentiment = gemini_ai.analyze_sentiment(content)
                logging.debug(f"Sentiment analysis: {sentiment}")
            except Exception as e:
                logging.error(f"Error analyzing sentiment: {str(e)}")
        
        db.session.add(new_feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('feedback.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        flash('Login successful!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
