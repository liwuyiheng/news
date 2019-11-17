import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from item.config import Config



app = Flask(__name__)


app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

# 初始化radis
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 初始化csrf
CSRFProtect(app)

# 初始化session
Session(app)