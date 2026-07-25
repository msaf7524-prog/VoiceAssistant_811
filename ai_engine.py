import requests


class AIEngine:

    def __init__(self, provider="groq", api_key=""):
        self.provider = provider
        self.api_key = api_key

    def set_provider(self, provider):
        self.provider = provider

    def set_api_key(self, api_key):
        self.api_key = api_key

    def ask(self, prompt):

        if self.provider == "groq":
            return self._groq(prompt)

        return "مزود الذكاء الاصطناعي غير مدعوم."

    def _groq(self, prompt):

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Voice Assistant 811."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.5
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                timeout=20
            )

            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            return f"AI Error: {e}"
