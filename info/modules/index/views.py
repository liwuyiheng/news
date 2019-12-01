from flask import render_template, current_app, session, g
# from sqlalchemy.sql.functions import user

from info import constants




from info.modules.passport.views import User
from info.utils.common import user_login_data
from . import index_blu




@index_blu.route('/')
@user_login_data
def index():
    user_id = session.get("user_id")
    # 通过id获取用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 获取点击排行数据
    news_list = None
    try:
        from info.models import News
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_basic_dict())


    # 获取新闻分类数据
    from info.models import Category
    categories = Category.query.all()
    # print(categories)
    # 定义列表保存分类数据
    categories_dicts = []

    for category in enumerate(categories):
        # 拼接内容
        categories_dicts.append(category[1].to_dict())
    data = {
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "categories": categories_dicts
    }
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")



