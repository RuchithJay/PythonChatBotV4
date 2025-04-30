import json
import random
from pathlib import Path

class ChatBot:
    def __init__(self, config_dir="config", config_file="responses.json"):
        self.config_path = Path(config_dir) / config_file
        self.responses = self._load_config()
        self.user_name = None
        self.context = {}

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            return self._get_default_responses()

    def _get_default_responses(self):
        return {
            "greetings": {"inputs": ["hello"], "outputs": ["Hi!"]},
            "goodbyes": {"inputs": ["bye"], "outputs": ["Goodbye!"]},
            "questions": {"default": ["I don't understand"]},
            "errors": {"empty_input": "Please type something"}
        }

    def _replace_placeholders(self, response):
        """Replace {name} placeholder with user's name if available"""
        if self.user_name and "{name}" in response:
            return response.replace("{name}", self.user_name)
        return response

    def _handle_personal_info(self, user_input):
        """Extract and store personal information like name"""
        name_keywords = ["my name is", "i am", "call me"]
        for keyword in name_keywords:
            if keyword in user_input.lower():
                self.user_name = user_input.lower().split(keyword)[1].strip().title()
                return random.choice(self.responses["personal"]["outputs"])
        return None

    def get_response(self, user_input):
        if not user_input.strip():
            return self.responses["errors"]["empty_input"]

        user_input = user_input.lower()
        
        # Check for personal information first
        personal_response = self._handle_personal_info(user_input)
        if personal_response:
            return self._replace_placeholders(personal_response)

        # Check all response categories
        categories = [
            ("greetings", self.responses["greetings"]["inputs"]),
            ("goodbyes", self.responses["goodbyes"]["inputs"]),
            ("compliments", self.responses.get("compliments", {}).get("inputs", [])),
            ("fun_phrases", self.responses.get("fun_phrases", {}).get("inputs", [])),
            ("tech", self.responses.get("tech", {}).get("inputs", []))
        ]

        for category, triggers in categories:
            if any(trigger in user_input for trigger in triggers):
                response = random.choice(self.responses[category]["outputs"])
                return self._replace_placeholders(response)

        # Check specific questions
        for question, answers in self.responses["questions"].items():
            if question != "default" and question in user_input:
                response = random.choice(answers)
                
                # Handle follow-up questions
                if question in self.responses.get("follow_ups", {}):
                    self.context["awaiting_follow_up"] = question
                    return f"{response} {self.responses['follow_ups'][question]['question']}"
                
                return self._replace_placeholders(response)

        # Handle follow-up responses
        if "awaiting_follow_up" in self.context:
            question = self.context.pop("awaiting_follow_up")
            if any(word in user_input for word in ["yes", "sure", "ok"]):
                return random.choice(self.responses["follow_ups"][question]["positive"])
            else:
                return random.choice(self.responses["follow_ups"][question]["negative"])

        # Default response
        return self._replace_placeholders(random.choice(self.responses["questions"]["default"]))

    def run(self):
        print(f"ChatBot: {random.choice(self.responses['greetings']['outputs'])}")
        
        while True:
            try:
                user_input = input("You: ")
                
                if any(goodbye in user_input.lower() for goodbye in self.responses["goodbyes"]["inputs"]):
                    print(f"ChatBot: {random.choice(self.responses['goodbyes']['outputs'])}")
                    break
                
                response = self.get_response(user_input)
                print(f"ChatBot: {response}")
                
            except KeyboardInterrupt:
                print("\nChatBot: Goodbye!")
                break
            except Exception as e:
                print(f"ChatBot: {self.responses['errors'].get('config_error', 'Something went wrong!')}")
                break

if __name__ == "__main__":
    bot = ChatBot()
    bot.run()