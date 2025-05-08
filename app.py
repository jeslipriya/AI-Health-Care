from flask import Flask, render_template, redirect, url_for,  request, flash,session, jsonify, send_file
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from datetime import datetime
import sqlite3
import logging
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import io


app = Flask(__name__)

# Set secret key and other configurations directly in the code
app.secret_key = 'jesli@07K'  # Replace with your secret key

# Flask-Mail Configuration for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jeslipriya07@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'ourb pzuz zfqn dhhb'    # Replace with your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'jeslipriya07@gmail.com'  # Replace with your email

mail = Mail(app)

# Database setup
DATABASE = 'users.db'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    """Creates the users and mood_data tables if they don't exist."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                blood_group TEXT,
                weight REAL,
                height REAL,
                phone TEXT,
                additional_phone TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                mood TEXT NOT NULL,
                mood_note TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error creating database tables: {e}")
    finally:
        conn.close()

create_table()

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """Executes a query with error handling and fetch options."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        data = None
        if fetchone:
            data = cursor.fetchone()
        elif fetchall:
            data = cursor.fetchall()
        
        conn.commit()
        return data
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None
    finally:
        conn.close()

# Set Gemini AI API Key directly in the code
GENAI_API_KEY = 'AIzaSyBOkqUQCMQHWjybckLUfov0SHMdYZvD_1g'  # Replace with your Gemini API key

# Configure the API
genai.configure(api_key=GENAI_API_KEY)

# Load the Gemini AI model gemini-1.5-pro
model = genai.GenerativeModel("gemini-1.5-pro")

# Function to filter health-related queries
def is_health_related(user_input):
    """Checks if the user input is related to health."""
    health_keywords = [
        "symptoms", "hi", "hello", "fever", "cough", "cold", "pain", "medicine", "doctor",
        "headache", "infection", "treatment", "allergy", "cancer", "diabetes",
        "blood pressure", "flu", "virus", "injury", "mental health", "anxiety", "thank you",
        "disease", "health", "diagnosis", "therapy", "vaccine", "nutrition", "thanks",
        "exercise", "diet", "heart", "lungs", "skin", "bones", "muscles","how are you"
    ]
    return any(word in user_input.lower() for word in health_keywords)

# Function to handle chatbot responses
def get_chatbot_response(user_input):
    """Generates a response from the Gemini AI model and formats it."""
    if not is_health_related(user_input):
        return "<p>Sorry, I can only help with health-related questions. 🩺 Try asking about symptoms, treatments, or anything medical!</p>"
    
    try:
        response = model.generate_content(user_input)
        formatted_response = response.text.replace('\n', '<br>')
        formatted_response = f"<p>{formatted_response}</p>"
        return formatted_response
    except Exception as e:
        logger.error(f"Error generating chatbot response: {e}")
        return f"<p>Error: {str(e)}</p>"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        try:
            execute_query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                          (username, email, hashed_password))
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = execute_query('SELECT * FROM users WHERE email = ?', (email,), fetchone=True)

        if user and check_password_hash(user[3], password):  # user[3] is password field
            session['user_id'] = user[0]  # Store user ID in session
            session['username'] = user[1]  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to access your profile.', 'error')
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/get_profile_data')
def get_profile_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    try:
        user = execute_query('SELECT * FROM users WHERE id = ?', (user_id,), fetchone=True)
        if user:
            return jsonify({
                'username': user[1],
                'email': user[2],
                'age': user[4] if user[4] is not None else '',
                'gender': user[5] if user[5] is not None else 'Male',
                'bloodGroup': user[6] if user[6] is not None else '',
                'weight': user[7] if user[7] is not None else '',
                'height': user[8] if user[8] is not None else '',
                'phone': user[9] if user[9] is not None else '',
                'additionalPhone': user[10] if user[10] is not None else '',
            })
        else:
            logger.error(f"User not found: user_id={user_id}")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching profile data: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
@app.route('/save_profile', methods=['POST'])
def save_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_id = session['user_id']

    try:
        execute_query('''
            UPDATE users SET
            age = ?,
            gender = ?,
            blood_group = ?,
            weight = ?,
            height = ?,
            phone = ?,
            additional_phone = ?
            WHERE id = ?
        ''', (
            data['age'],
            data['gender'],
            data['bloodGroup'],
            data['weight'],
            data['height'],
            data['phone'],
            data['additionalPhone'],
            user_id,
        ))
        return jsonify({'message': 'Profile updated successfully!'})
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/moodtracker')
def moodtracker():
    if 'user_id' not in session:
        flash('Please login to access the mood tracker.', 'error')
        return redirect(url_for('login'))
    return render_template('moodtracker.html')

@app.route('/save_mood', methods=['POST'])
def save_mood():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_id = session['user_id']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mood = data.get('mood')
    mood_note = data.get('moodNote', '')

    execute_query('INSERT INTO mood_data (user_id, timestamp, mood, mood_note) VALUES (?, ?, ?, ?)',
                  (user_id, timestamp, mood, mood_note))
    return jsonify({'message': 'Mood saved successfully!'})

@app.route('/get_mood_data', methods=['GET'])
def get_mood_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    mood_data = execute_query('SELECT timestamp, mood, mood_note FROM mood_data WHERE user_id = ?', (user_id,), fetchall=True)

    dates = [entry[0] for entry in mood_data]
    moods = [entry[1] for entry in mood_data]
    mood_history = [{'timestamp': entry[0], 'mood': entry[1], 'mood_note': entry[2]} for entry in mood_data]

    return jsonify({
        'dates': dates,
        'moods': moods,
        'moodHistory': mood_history,
    })

@app.route('/plot_mood_chart')
def plot_mood_chart():
    if 'user_id' not in session:
        print("Session:", session)
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    mood_data = execute_query('SELECT timestamp, mood FROM mood_data WHERE user_id = ?', (user_id,), fetchall=True)

    if not mood_data:
        return send_file('static/no_data.png', mimetype='image/png')  # Return a placeholder image if no data

    dates = [entry[0] for entry in mood_data]
    moods = [entry[1] for entry in mood_data]

    # Map mood strings to numerical values
    mood_to_number = {
        "Angry": 1,
        "Sad": 2,
        "Stressed": 3,
        "Neutral": 4,
        "Happy": 5,
    }
    mood_values = [mood_to_number[mood] for mood in moods]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, mood_values, marker='o', linestyle='-', color='b')
    plt.title('Mood Over Time')
    plt.xlabel('Date')
    plt.ylabel('Mood')
    plt.ylim(0, 6)
    plt.yticks([1, 2, 3, 4, 5], ["Angry", "Sad", "Stressed", "Neutral", "Happy"])
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

@app.route('/generate_health_tip', methods=['POST'])
def generate_health_tip():
    """Generates a health tip using Gemini AI based on user input."""
    data = request.get_json()
    user_input = data.get('user_input')

    if not user_input:
        return jsonify({'error': 'Please provide valid input.'}), 400

    try:
        # Generate a health tip using Gemini AI
        prompt = f"Generate a concise and actionable health tip for someone with the following goal or concern: {user_input}. The tip should be evidence-based and practical."
        response = model.generate_content(prompt)
        health_tip = response.text

        return jsonify({'health_tip': health_tip})
    except Exception as e:
        logger.error(f"Error generating health tip: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/healthtips')
def healthtips():
    return render_template('healthtips.html')

@app.route('/generate_diet_exercise_plan', methods=['POST'])
def generate_diet_exercise_plan():
    """Generate personalized diet and exercise recommendations."""
    data = request.get_json()
    user_profile = {
        'age': data.get('age'),
        'height': data.get('height'),
        'weight': data.get('weight'),
        'health_goals': data.get('health_goals'),
    }

    if not user_profile:
        return jsonify({
            "diet_plan": "Please complete your profile to receive personalized diet recommendations.",
            "exercise_plan": "Please complete your profile to receive personalized exercise recommendations."
        })

    # Create prompt for diet plan
    diet_prompt = f"""
    Create a personalized diet plan for someone with these characteristics:
    - Age: {user_profile.get('age', 'unknown')}
    - Height: {user_profile.get('height', 'unknown')} cm
    - Weight: {user_profile.get('weight', 'unknown')} kg
    - Health Goals: {user_profile.get('health_goals', 'general health')}
    
    Provide specific, actionable nutrition recommendations including:
    1. General dietary approach
    2. Recommended daily caloric intake (approximate)
    3. Macro distribution (protein, carbs, fats)
    4. Key foods to include
    5. Sample meal plan for one day
    
    Format the response in a clear, structured way with appropriate headings.
    """

    # Create prompt for exercise plan
    exercise_prompt = f"""
    Create a personalized exercise plan for someone with these characteristics:
    - Age: {user_profile.get('age', 'unknown')}
    - Height: {user_profile.get('height', 'unknown')} cm
    - Weight: {user_profile.get('weight', 'unknown')} kg
    - Health Goals: {user_profile.get('health_goals', 'general health')}
    
    Provide specific, actionable exercise recommendations including:
    1. Weekly workout structure
    2. Types of exercises recommended
    3. Duration and intensity guidelines
    4. Specific workout examples
    5. Safety considerations
    
    Format the response in a clear, structured way with appropriate headings.
    """

    try:
        # Generate diet and exercise plans using Gemini AI
        diet_response = model.generate_content(diet_prompt)
        exercise_response = model.generate_content(exercise_prompt)

        return jsonify({
            "diet_plan": diet_response.text,
            "exercise_plan": exercise_response.text
        })
    except Exception as e:
        logger.error(f"Error generating diet/exercise plan: {e}")
        return jsonify({
            "diet_plan": "Sorry, there was an error generating your diet plan.",
            "exercise_plan": "Sorry, there was an error generating your exercise plan."
        }), 500

@app.route('/dietandexercise')
def dietandexercise():
    return render_template('dietandexercise.html')

@app.route('/aichatbot', methods=['GET', 'POST'])
def aichatbot():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if not user_input:
            return jsonify({"response": "Please enter a valid question."})
        if not is_health_related(user_input):
            return jsonify({"response": "I can only answer health-related questions. Please ask about symptoms, diseases, or treatments."})
        response = get_chatbot_response(user_input)
        return jsonify({"response": response})
    return render_template('aichatbot.html')

@app.route('/hospitalfinder')
def hospitalfinder():
    if 'user_id' not in session:
        flash('Please login to access hospital finder.', 'error')
        return redirect(url_for('login'))
    return render_template('hospitalfinder.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/firstaid')
def firstaid():
    return render_template('firstaid.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    try:
        # Send email
        msg = Message(
            subject=f"Feedback from {name}",
            recipients=[app.config['MAIL_USERNAME']],  # Use the email from app config
            body=f"Name: {name}\nEmail: {email}\nMessage: {message}"
        )
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run()