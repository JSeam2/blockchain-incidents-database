import pymongo
import os

CONNECTION_STRING = "mongodb://localhost"  # replace it with your settings
CONNECTION = pymongo.MongoClient(CONNECTION_STRING)

'''Leave this as is if you dont have other configuration'''
DATABASE = CONNECTION.blog
POSTS_COLLECTION = DATABASE.posts
USERS_COLLECTION = DATABASE.users
SETTINGS_COLLECTION = DATABASE.settings

SECRET_KEY = ""
basedir = os.path.abspath(os.path.dirname(__file__))
secret_file = os.path.join(basedir, '.secret')

if os.path.exists(secret_file):
    # Read SECRET_KEY from .secret file
    with open(secret_file, 'rb') as f:
        SECRET_KEY = f.read().strip()

else:
    # Generate SECRET_KEY & save it away
    SECRET_KEY = os.urandom(24)
    with open(secret_file, 'wb') as f:
        f.write(SECRET_KEY)

    # Modify .gitignore to include .secret file
    gitignore_file = os.path.join(basedir, '.gitignore')
    with open(gitignore_file, 'a+') as f:
        if '.secret' not in f.readlines() and '.secret\n' not in f.readlines():
            f.write('.secret\n')

LOG_FILE = "app.log"

DEBUG = True  # set it to False on production
