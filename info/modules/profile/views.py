from flask import render_template, g, request, jsonify, current_app, session
from sqlalchemy.sql.functions import user
from werkzeug.utils import redirect

from info import constants, db
from info.models import Category, News
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@profile_blu.route('/info')
@user_login_data
def get_user_info():
    """
    获取用户信息
    1. 获取到当前登录的用户模型
    2. 返回模型中指定内容
    :return:
    """

    user = g.user
    if not user:
        # 用户未登录，重定向到主页
        return redirect('/')

    data = {
        "user_info": user.to_dict(),
    }
    # 渲染模板
    return render_template("news/user.html", data=data)


# @profile_blu.route('/user_info')
# @user_login_data
# def base_info():
#     """
#     用户基本信息
#     :return:
#     """
#     user = g.user
#     return render_template('news/user_base_info.html', data={"user_info": user.to_dict()})



@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    from info import db
    """
    用户基本信息
    1. 获取用户登录信息
    2. 获取到传入参数
    3. 更新并保存数据
    4. 返回结果
    :return:
    """

    # 1. 获取当前登录用户的信息
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user": user.to_dict()})


    # 2. 获取到传入参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")

    print(nick_name)
    print(signature)
    print(gender)
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in(['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3. 更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     db.session.rollback()
    #     return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    return render_template('news/user_pic_info.html', data={"user_info": user.to_dict()})

# 新闻关注
@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    # 取到当前登录用户
    user = g.user

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取当前页数据
        follows = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []

    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())

    data = {
        "users": user_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }

    return render_template('news/user_follow.html', data=data)

# 密码修改
@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    from info import db

    if request.method == "GET":
        return render_template('news/user_pass_info.html')

        # 1. 获取到传入参数

    data_dict = request.json
    old_password = data_dict.get("old_password")
    new_password = data_dict.get("new_password")
    print(old_password)
    print(new_password)
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2. 获取当前登录用户的信息
    user = g.user

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    # 更新数据
    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="保存成功")

# 我的收藏
@profile_blu.route('/collection')
@user_login_data
def user_collection():

    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user
    collections = []
    current_page = 1
    total_page = 1
    try:
        # 进行分页数据查询
        paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取分页数据
        collections = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 收藏列表
    collection_dict_li = []
    for news in collections:
        collection_dict_li.append(news.to_basic_dict())

    data = {"total_page": total_page, "current_page": current_page, "collections": collection_dict_li}

    return render_template('news/user_collection.html',data=data)

# 新闻发布

@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        categories = []
        try:
            # 获取所有的分类数据
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        # 定义列表保存分类数据
        categories_dicts = []

        for category in categories:
            # 获取字典
            cate_dict = category.to_dict()
            # 拼接内容
            categories_dicts.append(cate_dict)

        # 移除`最新`分类
        categories_dicts.pop(0)
        # 返回内容
        return render_template('news/user_news_release.html', data={"categories": categories_dicts})
    # POST 提交，执行发布新闻操作

    # 1. 获取要提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    print(title)
    print(digest)
    print(content)
    print(index_image)
    print(category_id)
    # 1.1 判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 1.2 尝试读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # # 2. 将标题图片上传到七牛
    # try:
    #     key = storage(index_image)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 3. 初始化新闻模型，并设置相关数据
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    # news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表待审核状态
    news.status = 1

    # 4. 保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 5. 返回结果
    return jsonify(errno=RET.OK, errmsg="发布成功，等待审核")


# 新闻列表

@profile_blu.route('/news_list')
@user_login_data
def news_list():
    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user
    news_li = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())
    data = {"news_list": news_dict_li, "total_page": total_page, "current_page": current_page}
    return render_template('news/user_news_list.html', data=data)