import requests
import unicodedata
from difflib import get_close_matches

class ClassifierAgent:
    def __init__(self, model="mistral", port=11434):
        self.url = f"http://localhost:{port}/api/generate"
        self.model = model

    def strip_accents(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')

    def normalize_final_sigma(self, word):
        return word.replace('ς', 'σ')

    def classify(self, prompt):
        # 🔹 Προεπεξεργασία φυσικής γλώσσας
        prompt = self.strip_accents(prompt.lower())

        keywords_blocks = ['μπλοκ', 'block', 'στοιβα', 'stoiv', 'stoives']
        keywords_jugs = ['δοχειο', 'νερο', 'jug', 'κουβα', 'bucket', 'litro', 'λιτρα']

        # 🔍 Πρώτα: fuzzy match με τις λέξεις στο prompt
        for word in prompt.split():
            word = self.normalize_final_sigma(word)
            if get_close_matches(word, keywords_blocks, cutoff=0.7):
                return 'blocks'
            if get_close_matches(word, keywords_jugs, cutoff=0.7):
                return 'jug'

        # 🤖 Fallback σε LLM (αν δεν πιάσει τίποτα)
        system_prompt = (
            "Ανάλυσε το παρακάτω κείμενο και απάντησε ΜΟΝΟ με μία λέξη:\n"
            "- blocks (για πρόβλημα με στοίβες/μπλοκ)\n"
            "- jug (για πρόβλημα με λίτρα/δοχεία)\n"
            "- unknown (αν δεν μπορείς να αποφασίσεις)\n"
            "ΜΗΝ εξηγείς τίποτα, γράψε μόνο τη λέξη."
        )
        full_prompt = f"{system_prompt}\n\nΚείμενο:\n{prompt}"

        try:
            response = requests.post(self.url, json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            })
            response.raise_for_status()
            return response.json()["response"].strip().lower()
        except Exception as e:
            print(" Σφάλμα επικοινωνίας με το Ollama:", e)
            return "unknown"
