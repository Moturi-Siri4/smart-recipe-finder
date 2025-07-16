from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import markdown
from search_engine import SearchEngine
from mistral_handler import get_response, generate_tts
import os
from datetime import datetime

app = Flask(__name__)
engine = SearchEngine()

# In-memory storage for feedback
feedback_list = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    query = request.form.get('query', '')
    ingredients = request.form.get('ingredients', '')
    tts = request.form.get('tts', 'true').lower() == 'true'  # Get TTS preference from form
    
    if query:
        response_data = engine.query(query)
    elif ingredients:
        response_data = engine.query("", ingredients=ingredients)
    else:
        return redirect(url_for('index'))
    
    if not response_data or not response_data[0]:
        return render_template('results.html', 
                            recipes='No matching recipes found.',
                            tts=False)
    
    # Convert markdown to HTML for display
    html_recipes = markdown.markdown(response_data[0])
    audio_url = None
    
    if tts:
        # Clean the text for TTS by removing markdown formatting
        import re
        clean_text = re.sub(r'#+\s*', '', response_data[0])  # Remove headers
        clean_text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', clean_text)  # Remove bold/italic
        clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean_text)  # Remove links
        clean_text = re.sub(r'`{3}.*?`{3}', '', clean_text, flags=re.DOTALL)  # Remove code blocks
        clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)  # Remove inline code
        clean_text = re.sub(r'^\s*[\-\*\+]\s*', '', clean_text, flags=re.MULTILINE)  # Remove list markers
        
        print(f"Cleaned text for TTS: {clean_text[:200]}...")  # Debug log
        audio_path = generate_tts(clean_text)
        if audio_path:
            print(f"Generated TTS audio at: {audio_path}")  # Debug log
            if os.path.exists(audio_path):
                print("Audio file exists")  # Debug log
                audio_url = f'/tts/{os.path.basename(audio_path)}'
                print(f"Serving audio at: {audio_url}")  # Debug log
            else:
                print("ERROR: Audio file not found")  # Debug log
    
    return render_template('results.html',
                         recipes=html_recipes,
                         audio_url=audio_url,
                         tts=tts)

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query = data.get('query', '')
    tts = data.get('tts', False)
    print(f"Received query: {query}")  # Debugging log
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    response_data = engine.query(query)
    if not response_data or not response_data[0]:
        return jsonify({'result': 'No matching recipes found.'})
    
    html_recipes = markdown.markdown(response_data[0])
    response = {'recipes': html_recipes}
    
    if tts:
        audio_path = generate_tts(response_data[0])
        if audio_path:
            response['audio_url'] = f'/tts/{os.path.basename(audio_path)}'
    
    return jsonify(response)

@app.route('/leftovers', methods=['POST'])
def leftovers():
    data = request.get_json()
    ingredients = data.get('ingredients', '')
    tts = data.get('tts', False)
    print(f"Received ingredients: {ingredients}")
    if not ingredients:
        return jsonify({'error': 'No ingredients provided'}), 400
    
    response_data = engine.query("", ingredients=ingredients)
    if not response_data or not response_data[0]:
        return jsonify({'result': 'No matching recipes found.'})
    
    html_recipes = markdown.markdown(response_data[0])
    response = {'recipes': html_recipes}
    
    if tts:
        audio_path = generate_tts(response_data[0])
        if audio_path:
            response['audio_url'] = f'/tts/{os.path.basename(audio_path)}'
    
    return jsonify(response)

@app.route('/tts/<filename>')
def serve_audio(filename):
    try:
        audio_path = os.path.join(os.path.dirname(__file__), 'tts_test', filename)
        print(f"Serving audio file from: {audio_path}")  # Debugging log
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            return jsonify({'error': 'Audio file not found'}), 404
        return send_file(audio_path, mimetype='audio/mpeg')
    except FileNotFoundError:
        return jsonify({'error': 'Audio file not found'}), 404

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback = request.form.get('feedback', '')
    rating = request.form.get('rating', '0')
    feedback_list.append({
        'feedback': feedback,
        'rating': rating,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    print(f"Received feedback: {feedback} with rating: {rating}")  # Log feedback to console
    return redirect(url_for('thank_you'))  # Redirect to thank you page

@app.route('/thank_you')
def thank_you():
    return render_template('feedback.html')

@app.route('/view_feedback')
def view_feedback():
    return render_template('view_feedback.html', feedbacks=feedback_list)

@app.route('/meal-plan')
def meal_plan():
    return render_template('meal_plan.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    data = request.get_json()
    preferences = data.get('preferences', [])
    restrictions = data.get('restrictions', [])
    
    # Create a query that includes dietary preferences and restrictions
    query = "Generate a weekly meal plan with breakfast, lunch, and dinner for each day. "
    
    if preferences:
        query += f"Dietary preferences: {', '.join(preferences)}. "
    if restrictions:
        query += f"Dietary restrictions: {', '.join(restrictions)}. "
    
    query += "Please provide recipes that are diverse and balanced."
    
    # Get response from the search engine
    response_data = engine.query(query)
    
    if not response_data or not response_data[0]:
        return jsonify({'error': 'Failed to generate meal plan'}), 500
    
    # Parse the response into a structured meal plan
    # This is a simplified example - you might want to add more sophisticated parsing
    meal_plan = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meals = ['Breakfast', 'Lunch', 'Dinner']
    
    # Split the response into sections for each day
    response_text = response_data[0]
    for day in days:
        day_meals = []
        for meal in meals:
            # Extract meal name and description
            # This is a simple implementation - you might want to improve the parsing
            meal_text = f"{meal}: "
            start_idx = response_text.find(meal_text)
            if start_idx != -1:
                end_idx = response_text.find('\n', start_idx)
                if end_idx == -1:
                    end_idx = len(response_text)
                meal_description = response_text[start_idx + len(meal_text):end_idx].strip()
                day_meals.append(meal_description)
            else:
                day_meals.append("No recipe found")
        meal_plan.append(day_meals)
    
    return jsonify({'meal_plan': meal_plan})

if __name__ == "__main__":
    app.run(debug=True)
