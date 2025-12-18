from django.conf import settings
from pymongo import MongoClient

_client = None


def get_mongo_client():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client


def get_mongo_db():
    return get_mongo_client()[settings.MONGODB_NAME]


def forms_collection():
    return get_mongo_db()["forms"]

def field_collection():
    return get_mongo_db()["fields"]

def submissions_collection():
    return get_mongo_db()["submissions"]