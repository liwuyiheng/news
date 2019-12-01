from _codecs import decode

import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import Config
from config import config
import logging
from logging.handlers import RotatingFileHandler
from info.modules.index import index_blu
from info.modules.passport import passport_blu
redis_store = redis.StrictRedis(host=config["development"].REDIS_HOST, port=config["development"].REDIS_PORT,decode_responses = True)
db = SQLAlchemy()


from flask_wtf.csrf import generate_csrf








def create_app(config_name):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""
    app = Flask(__name__)


    app.config.from_object(config[config_name])

    # 初始化数据库
    db.init_app(app)

    # 初始化radis
    # global redis_store
    # redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)

    # 初始化csrf
    # CSRFProtect(app)
    # 导入生成 csrf_token 值的函数
    # 调用函数生成 csrf_token
    # csrf_token = generate_csrf()

    # 初始化session
    Session(app)
    # 配置日志
    setup_log(config_name)


    # 注册蓝图
    app.register_blueprint(index_blu)
    app.register_blueprint(passport_blu)

    from info.modules.news import news_blu
    app.register_blueprint(news_blu)
    return app


def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)