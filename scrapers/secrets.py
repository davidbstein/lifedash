import json
import os

SECRETS = json.load(open(os.path.dirname(__file__) + "/../secrets.json"))
SETTINGS = json.load(open(os.path.dirname(__file__) + "/../settings.json"))
