from flask import render_template, current_app, session, g, request, jsonify
# from sqlalchemy.sql.functions import user

from info import constants


from info.modules.passport.views import User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/new_list')
def new_list():
    from info.models import News
    # 1. 获取参数
    # 新闻的分类id
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    # 2. 校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数")

    filters = [News.status == 0]
    if cid != 1:  # 查询的不是最新的数据
        # 需要添加条件
        filters.append(News.category_id == cid)

    # 3. 查询数据

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 取到当前页的数据
    news_model_list = paginate.items  # 模型对象列表
    total_page = paginate.pages
    current_page = paginate.page

    # 将模型对象列表转成字典列表
    news_dict_li = []
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_li": news_dict_li
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)


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

    # 定义列表保存分类数据
    categories_dicts = []

    for category in enumerate(categories):
        # 拼接内容
        categories_dicts.append(category[1].to_dict())
        # print(category)
    data = {
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "categories": categories_dicts
    }
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")



