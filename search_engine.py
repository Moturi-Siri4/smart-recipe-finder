from mistral_handler import get_response

class SearchEngine:
    def __init__(self):
        print("Search Engine Initialized...")

    def query(self, text, ingredients=None):
        return get_response(text, ingredients=ingredients)  # Pass ingredients to handler
