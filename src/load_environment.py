import os
from dotenv import load_dotenv

class LoadEnv:
    def __init__(self):
        self._load_env_file()
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.HF_TOKEN = os.getenv("HF_TOKEN")

    def _load_env_file(self):
        if os.path.exists(".env.local"):
            load_dotenv('.env.local')
            print("local env loaded")
        elif os.path.exists(".env"):
            load_dotenv(".env")
        else:
            print("env file does not exist")

load_env = LoadEnv()