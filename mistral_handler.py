from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from gtts import gTTS
import os
import tempfile

API_KEY = "R64Mwj4jGTDeZcGj6c40v5djcImVfikB"  # Replace with your actual Mistral API key
client = MistralClient(api_key=API_KEY)

def generate_tts(text, lang='en'):
    """Convert text to speech and return the audio file path"""
    print(f"Generating TTS for text: {text[:50]}...")  # Debugging log
    try:
        # Use fixed test location
        test_dir = os.path.join(os.path.dirname(__file__), 'tts_test')
        os.makedirs(test_dir, exist_ok=True)
        path = os.path.join(test_dir, 'test_audio.mp3')
        
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(path)
        
        # Verify file was created and has content
        if not os.path.exists(path):
            print("Error: Audio file was not created.")
            return None
            
        file_size = os.path.getsize(path)
        print(f"Audio file created at: {path} (Size: {file_size} bytes)")
        
        if file_size < 1024:  # Minimum reasonable size for short audio
            print("Warning: Audio file may be empty or corrupted")
            
        return path
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None

def get_response(prompt, tts=False, ingredients=None):
    # Define the bot's role and scope using a system message
    system_content = (
        "You are a Michelin-star Indian chef and culinary expert. You exclusively use the SI Metric system for all measurements. "

        "You provide expert advice on recipes, cooking techniques, ingredient pairings, meal planning, nutrition analysis, and ingredient pricing. "

        "You can suggest recipes based on available ingredients, dietary preferences, and cooking styles, as well as analyze the nutritional content and cost of dishes in indian rupees. "

        "If the question is unrelated to cooking or food, politely steer the conversation back to culinary topics. "
    )
    
    if ingredients:
        system_content += (
            " The user is asking for recipes using leftover ingredients. "
            "Prioritize recipes that use all or most of these ingredients: " + ingredients + ". "
            "Suggest creative ways to combine them and mention any small additional ingredients needed."
        )
        prompt = f"Suggest recipes using these leftover ingredients: {ingredients}"

    system_message = ChatMessage(
        role="system",
        content=system_content + " Please format all responses in Markdown."
    )
    
    user_message = ChatMessage(role="user", content=prompt)
    
    messages = [system_message, user_message]

    response = client.chat(model="mistral-medium", messages=messages)
    
    answer = response.choices[0].message.content

    if tts:
        audio_path = generate_tts(answer)
        return answer, audio_path
    
    return answer, None

# Example use:
# prompt = "I have chicken, garlic, and rice. What can I make?"
# response = get_response(prompt)
# print(response)
