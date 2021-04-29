import pymongo
import os

MONGO_URI = "mongodb://{}:{}@{}:{}/{}".format(
    os.getenv('MONGO_USERNAME'),
    os.getenv('MONGO_PASSWORD'),
    os.getenv('MONGO_HOST'),
    os.getenv('MONGO_PORT'),
    os.getenv('MONGO_AUTH_SOURCE')
)
db = pymongo.MongoClient(MONGO_URI)[os.getenv('MONGO_AUTH_SOURCE')]

