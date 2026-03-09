import requests

class AIService:

    def __init__(self):
        self.url = "https://preflagellate-korbin-rateably.ngrok-free.dev/generate"

    def ask(self, message):

        response = requests.post(
            self.url,
            params={"prompt": message}
        )

        return response.json()