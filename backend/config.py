
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pc28.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    # Poll interval in seconds (shorter = more realtime)
    POLL_INTERVAL = 5 
    # External lottery API config
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://hanxin28.com/api/api.php')
    API_TOKEN = os.environ.get('API_TOKEN', '9ecd478bd3bbfb4ca1e48954b8beda13')
    GAME_TYPE = os.environ.get('GAME_TYPE', 'jnd28')
    HISTORY_FETCH_LIMIT = int(os.environ.get('HISTORY_FETCH_LIMIT', 100))
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 10))
