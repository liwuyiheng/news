from flask import render_template, g, request, jsonify, current_app, session
from sqlalchemy.sql.functions import user
from werkzeug.utils import redirect


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
        "user": user.to_dict(),
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
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    return render_template('news/user_pic_info.html', data={"user": user.to_dict()})


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    from info import db
    print(request.method)
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

