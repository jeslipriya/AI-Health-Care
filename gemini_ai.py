import os
import json
import google.generativeai as genai
from PIL import Image
import base64
import io

# Configure the Gemini API with your key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# List available models for debugging
try:
    available_models = [model.name for model in genai.list_models()]
    print(f"Available Gemini models: {available_models}")
except Exception as e:
    print(f"Error listing models: {e}")

# Default model to use - based on available models
DEFAULT_MODEL = "models/gemini-1.5-pro"  # Using the available stable model from the list
DEFAULT_IMAGE_MODEL = "models/gemini-1.5-pro-vision-latest"  # Using the available vision model

def generate_text(prompt, temperature=0.7, max_tokens=1024):
    """
    Generate text response using Gemini Pro model
    
    Args:
        prompt (str): The prompt to send to the model
        temperature (float): Controls randomness (0.0 to 1.0)
        max_tokens (int): Maximum length of the response
        
    Returns:
        str: The generated text response
    """
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        return f"I apologize, but I encountered an error: {str(e)}"

def generate_json(prompt, temperature=0.2):
    """
    Generate a structured JSON response
    
    Args:
        prompt (str): Prompt describing the needed JSON structure
        temperature (float): Controls randomness, lower for more deterministic outputs
        
    Returns:
        dict: Parsed JSON object
    """
    try:
        # Add explicit instructions to format as JSON
        json_prompt = f"{prompt}\n\nRespond with a valid JSON object only, no additional text."
        
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(
            json_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )
        
        # Parse the response text as JSON
        json_response = json.loads(response.text)
        return json_response
    except json.JSONDecodeError:
        # If we can't parse the JSON, try to extract it from text with brackets
        try:
            # Try to extract JSON object from the text if surrounded by other text
            text = response.text
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            return {"error": "Could not parse response as JSON"}
        except Exception as e:
            return {"error": f"JSON parsing error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error generating JSON: {str(e)}"}

def analyze_image(base64_image, prompt="Describe this image in detail"):
    """
    Analyze image content using Gemini Pro Vision model
    
    Args:
        base64_image (str): Base64 encoded image
        prompt (str): Prompt for analysis instructions
        
    Returns:
        str: Text analysis of the image
    """
    try:
        # Decode the base64 image
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        
        # Create a model instance with Gemini Pro Vision
        model = genai.GenerativeModel(DEFAULT_IMAGE_MODEL)
        
        # Generate content with the image and prompt
        response = model.generate_content([prompt, image])
        
        return response.text
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return f"I encountered an error analyzing this image: {str(e)}"

def summarize_article(text):
    """
    Summarize a longer text or article
    
    Args:
        text (str): The text to summarize
        
    Returns:
        str: A concise summary
    """
    prompt = f"Please summarize the following text concisely while maintaining key points:\n\n{text}"
    return generate_text(prompt, temperature=0.3)

def analyze_sentiment(text):
    """
    Analyze sentiment of text and provide a rating
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Sentiment analysis results with rating and confidence
    """
    prompt = """
    Analyze the sentiment of the following text and provide a rating from 1 to 5 stars
    and a confidence score between 0 and 1. Respond with JSON in this format:
    {'rating': number, 'confidence': number}
    
    Text to analyze:
    """ + text
    
    result = generate_json(prompt, temperature=0.1)
    
    # Ensure values are in correct range and proper types
    if 'rating' in result:
        try:
            # Convert to float first to handle any non-integer values
            rating_value = float(result['rating'])
            result['rating'] = max(1, min(5, int(round(rating_value))))
        except (ValueError, TypeError):
            # Set a default if conversion fails
            result['rating'] = 3
            
    if 'confidence' in result:
        try:
            # Convert to float and ensure it's between 0 and 1
            confidence_value = float(result['confidence'])
            result['confidence'] = max(0.0, min(1.0, confidence_value))
        except (ValueError, TypeError):
            # Set a default if conversion fails
            result['confidence'] = 0.5
    
    return result

def health_conversation(message, context=None):
    """
    Have a health-focused conversation with appropriate medical disclaimers
    
    Args:
        message (str): User's message or question
        context (str): Optional prior conversation context
        
    Returns:
        str: AI response focused on health information
    """
    system_context = """
    You are an AI health assistant providing general health information and guidance.
    Important disclaimers:
    1. You are not a doctor and don't provide medical diagnosis or treatment
    2. Always advise users to consult healthcare professionals for medical concerns
    3. Provide evidence-based information on general health topics
    4. Focus on wellness, prevention, and healthy lifestyle choices
    5. For any concerning symptoms or medical emergencies, direct users to seek immediate medical care
    
    Respond with helpful, accurate health information while maintaining these guidelines.
    """
    
    # Combine context if provided
    if context:
        prompt = f"{system_context}\n\nPrevious conversation:\n{context}\n\nUser: {message}\nAI:"
    else:
        prompt = f"{system_context}\n\nUser: {message}\nAI:"
    
    return generate_text(prompt, temperature=0.7)

def generate_health_tip(user_profile=None):
    """
    Generate personalized health tip based on user profile if available
    
    Args:
        user_profile (dict): Optional user profile data
        
    Returns:
        str: Personalized health tip
    """
    if user_profile:
        prompt = f"""
        Generate a helpful health tip for a user with the following profile:
        - Age: {user_profile.get('age', 'unknown')}
        - Goals: {user_profile.get('health_goals', 'general health improvement')}
        
        The health tip should be evidence-based, actionable, and specific to their profile.
        Keep it concise (1-2 paragraphs) and focus on practical advice they can implement.
        """
    else:
        prompt = """
        Generate a helpful general health tip that would benefit most people.
        The health tip should be evidence-based, actionable, and practical.
        Keep it concise (1-2 paragraphs) and focus on everyday health improvements.
        """
    
    return generate_text(prompt, temperature=0.7)

def generate_diet_exercise_plan(user_profile):
    """
    Generate personalized diet and exercise recommendations
    
    Args:
        user_profile (dict): User profile with age, height, weight, goals
        
    Returns:
        dict: Diet and exercise recommendations
    """
    if not user_profile:
        return {
            "diet_plan": "Please complete your profile to receive personalized diet recommendations.",
            "exercise_plan": "Please complete your profile to receive personalized exercise recommendations."
        }
    
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
    
    # Generate both plans
    try:
        diet_plan = generate_text(diet_prompt, temperature=0.3)
        exercise_plan = generate_text(exercise_prompt, temperature=0.3)
        
        return {
            "diet_plan": diet_plan,
            "exercise_plan": exercise_plan
        }
    except Exception as e:
        print(f"Error generating diet/exercise plan: {e}")
        return {
            "diet_plan": "Sorry, there was an error generating your diet plan.",
            "exercise_plan": "Sorry, there was an error generating your exercise plan."
        }