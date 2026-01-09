from pymongo import MongoClient
from config import MONGO_URL

mongo = MongoClient(MONGO_URL)
db = mongo["advanced_ref_bot"]

users = db["users"]
special_links = db["special_links"]
withdraws = db["withdraws"]
