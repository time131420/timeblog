from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g,abort
from werkzeug.security import generate_password_hash, check_password_hash

import sys
sys.path.append('..')
from Model import ConfigModel, UserAdminModel, articleModel, NavModel,blogrollModel
from decorator import admin_login_required
from extension import db

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.before_request
def before_request():
    user_id = session.get('userAdmin_id')
    if user_id:
        try:
            user = UserAdminModel().query.get(user_id)
            g.userAdmin = user
        except:
            g.userAdmin = None
    cf = ConfigModel().query.get(1)
    ip_list = cf.Whitea_list.split(',')
    if ip_list != [''] and ip_list != None:
        for i in ip_list:
            if i != request.remote_addr:
                abort(404)

# 404
@bp.errorhandler(404)
def errorhandler(error):
    return render_template('error/404.html'),404


@bp.route('/')
@admin_login_required
def index():
    return render_template('admin/index/index.html')


# 管理登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        usermodel = UserAdminModel.query.filter_by(username=username).first()
        if usermodel and check_password_hash(usermodel.password, request.form.get('password')) and usermodel.state == 1:
            session['userAdmin_id'] = usermodel.id
            session.get('userAdmin_id')
            # session['username'] = username
            # session['type'] = usermodel.type
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('admin.login'))
    else:
        return render_template('admin/index/login.html')


# 管理注销登陆
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


# 编辑网站配置
@bp.route('/editConfig', methods=['GET', 'POST'])
@admin_login_required
def editConfig():
    if request.method == 'POST':
        db.session.query(ConfigModel).filter(ConfigModel.id == 1).update(request.form)
        db.session.commit()
        flash("网站信息编辑成功！")
        return redirect(url_for('admin.editConfig'))
    else:
        config = ConfigModel.query.get(1)
        return render_template('admin/editConfig.html', config=config)


# 文章列表
@bp.route('/article/list', methods=['GET', 'POST'])
@admin_login_required
def article_list():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    if request.args.get("delete") != None:
        data = articleModel.query.get(request.args.get("delete"))
        db.session.delete(data)
        db.session.commit()
        flash("删除成功")
        return redirect(url_for('admin.article_list'))
    elif request.args.get("article_show") != None and request.args.get("show") != None:
        data = articleModel.query.get(request.args.get("article_show"))
        data.article_show = request.args.get("show")
        db.session.add(data)
        db.session.commit()
        flash("显示状态修改成功")
        return redirect(url_for('admin.article_list'))
    elif request.args.get("id") != None and request.args.get("encryption") != None:
        data = articleModel.query.get(request.args.get("id"))
        data.article_encryption = request.args.get("encryption")
        db.session.add(data)
        db.session.commit()
        flash("加密状态修改成功")
        return redirect(url_for('admin.article_list'))
    elif request.args.get('eidt') != None:
        if request.method == 'POST':
            db.session.query(articleModel).filter(articleModel.id == request.args.get("eidt")).update(request.form)
            db.session.commit()
            return redirect(url_for('admin.article_list'))
        else:
            data = articleModel.query.get(request.args.get("eidt"))
            nav_bar = NavModel.query.all()
            return render_template('admin/article/eidt.html', article=data, nav_bar=nav_bar)
    page_size = ConfigModel.query.get(1).number_pages
    search = request.args.get('search')
    if search != None:
        article_list = articleModel.query.filter(articleModel.article_title.like(f'%{search}%')).limit(page_size).limit(page_size).offset((page-1)*page_size).all()
        count = articleModel.query.filter(articleModel.article_title.like(f'%{search}%')).count()
        count = len([i+1 for i in range(int(count/page_size))])
    else:
        article_list = articleModel.query.all()
        count = len([i + 1 for i in range(int(len(article_list) / page_size))])
        search = 0
    return render_template('admin/article/index.html', article_list=article_list,count=count,number=search)


# 添加文章
@bp.route('/article/add', methods=['GET', 'POST'])
@admin_login_required
def article_add():
    if request.method == 'POST':
        form = request.form
        article_title = form.get('article_title')
        article_content = form.get('article_content')
        article_img = form.get('article_img')
        article_introduce = form.get('article_introduce')
        article_show = form.get('article_show')
        article_encryption = form.get('article_encryption')
        encryption_code = form.get('encryption_code')
        nav_bar_id = form.get('nav_bar_id')
        articleModels = articleModel(article_title=article_title, article_content=article_content,
                                     article_img=article_img, article_introduce=article_introduce,
                                     article_show=article_show, article_encryption=article_encryption,
                                     encryption_code=encryption_code, nav_bar_id=nav_bar_id)
        db.session.add(articleModels)
        db.session.commit()
        return redirect(url_for('admin.article_list'))

    else:
        nav_bar = NavModel.query.all()
        return render_template('admin/article/add.html', nav_bar=nav_bar)


# 管理员修改密码
@bp.route('eidtpwd', methods=['GET', 'POST'])
@admin_login_required
def eidtpwd():
    if request.method == 'POST':
        form = request.form
        id = session.get('userAdmin_id')
        user = UserAdminModel().query.get(id)
        if check_password_hash(user.password, form.get('oldpwd')) != True:
            flash('原密码错误')
            return redirect(url_for('admin.eidtpwd'))
        elif form.get('newpwd') != form.get('confirmpwd'):
            flash('两次密码不一致')
            return redirect(url_for('admin.eidtpwd'))
        elif form.get('oldpwd') == form.get('newpwd'):
            flash('新密码与旧密码相同')
            return redirect(url_for('admin.eidtpwd'))
        else:
            user.password = generate_password_hash(form.get('newpwd'))
            db.session.add(user)
            db.session.commit()
            session.clear()
            return redirect(url_for('admin.login'))
    else:
        return render_template('admin/superuser/editPassword.html')


# 管理员列表
@bp.route('/superuser/list', methods=['GET', 'POST'])
@admin_login_required
def superuser_list():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    if request.args.get('delete') != None and request.args.get('delete') != '1':
        user = UserAdminModel().query.get(request.args.get('delete'))
        db.session.delete(user)
        db.session.commit()
        flash(f"{user.username}删除完成")
        return redirect(url_for('admin.superuser_list'))
    elif request.args.get('id') != None and request.args.get('state') != None:
        if request.args.get('id') == '1':
            flash(f"超级管理员不允许修改")
            return redirect(url_for('admin.superuser_list'))
        else:
            user = UserAdminModel().query.get(request.args.get('id'))
            user.state = request.args.get('state')
            db.session.add(user)
            db.session.commit()
            flash(f"{user.username}状态修改完成")
            return redirect(url_for('admin.superuser_list'))
    elif request.args.get('editpwd') != None:
        if request.method == 'POST':
            if request.args.get('editpwd') == '1':
                return redirect(url_for('admin.superuser_list'))
            else:
                db.session.query(UserAdminModel).filter(UserAdminModel.id == request.args.get('editpwd')).update(request.form)
                db.session.commit()
                return redirect(url_for('admin.superuser_list'))
        else:
            user = UserAdminModel().query.get(request.args.get('editpwd'))
            return render_template('admin/superuser/editpwd.html',user=user)
    page_size = ConfigModel.query.get(1).number_pages
    search = request.args.get('search')
    if search != None:
        data = UserAdminModel.query.filter(UserAdminModel.username.like(f'%{search}%')).limit(page_size).offset((page-1)*page_size).all()
        # data = UserAdminModel.query.filter(UserAdminModel.username.like(f'%{search}%')).limit(page_size).offset((page-1)*page_size).all()
        print(data)
        count = UserAdminModel.query.filter(UserAdminModel.username.like(f'%{search}%')).count()
        count = len([i+1 for i in range(int(count/page_size))])
    else:
        data = UserAdminModel.query.all()
        count = len([i + 1 for i in range(int(len(data) / page_size))])
        search = 0
    return render_template('admin/superuser/index.html', superuser=data,count=count,number=search)


# 添加管理员
@bp.route('/superuser/add', methods=['GET', 'POST'])
@admin_login_required
def superuser_add():
    if request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = generate_password_hash(form.get('password'))
        name = form.get('name')
        type = form.get('type')
        user = UserAdminModel(username=username, password=password, name=name, type=type)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.superuser_list'))
    else:
        return render_template('admin/superuser/add.html')


# 导航条列表
@bp.route('/navigation/list', methods=['GET', 'POST'])
@admin_login_required
def navigation_list():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    if request.args.get('delete') != None and request.args.get('delete') != '1':
        user = NavModel().query.get(request.args.get('delete'))
        db.session.delete(user)
        db.session.commit()
        flash(f"{user.nav_name}删除完成")
        return redirect(url_for('admin.navigation_list'))
    elif request.args.get('id') != None and request.args.get('state') != None:
        user = NavModel().query.get(request.args.get('id'))
        user.state = request.args.get('state')
        db.session.add(user)
        db.session.commit()
        date = articleModel().query.filter(articleModel.nav_bar_id == request.args.get('id')).all()
        for article in date:
            article.article_show = int(request.args.get('state'))
        # db.session.add(date)
        db.session.commit()
        flash(f"{user.nav_name}状态修改完成")
        return redirect(url_for('admin.navigation_list'))
    elif request.args.get('edit') != None:
        if request.method == 'POST':
            db.session.query(NavModel).filter(NavModel.id == request.args.get('edit')).update(request.form)
            db.session.commit()
            return redirect(url_for('admin.navigation_list'))
        else:
            nav = NavModel().query.get(request.args.get('edit'))
            return render_template('admin/nav/edit.html',nav=nav)
    page_size = ConfigModel.query.get(1).number_pages
    search = request.args.get('search')
    if search != None:
        data = NavModel.query.filter(NavModel.nav_name.like(f'%{search}%')).limit(page_size).limit(page_size).offset((page-1)*page_size).all()
        count = NavModel.query.filter(NavModel.nav_name.like(f'%{search}%')).count()
        count = len([i+1 for i in range(int(count/page_size))])
    else:
        data = NavModel.query.all()
        count = len([i + 1 for i in range(int(len(data) / page_size))])
        search = 0
    return render_template('admin/nav/index.html', navigation=data,count=count,number=search)

# 添加导航条
@bp.route('/navigation/add', methods=['GET', 'POST'])
@admin_login_required
def navigation_add():
    if request.method == 'POST':
        name = request.form.get('nav_name')
        nav_href = request.form.get('nav_href')
        state = request.form.get('state')
        data = NavModel(nav_name=name,nav_href=nav_href,state=state)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('admin.navigation_list'))
    else:
        return render_template('admin/nav/add.html')

# 友链列表
@bp.route('/blogroll/list', methods=['GET', 'POST'])
@admin_login_required
def blogroll_list():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    if request.args.get('delete') != None:
        data = blogrollModel().query.get(request.args.get('delete'))
        db.session.delete(data)
        db.session.commit()
        flash(f"{data.name}删除完成")
        return redirect(url_for('admin.blogroll_list'))
    elif request.args.get('id') != None and request.args.get('state') != None:
        data = blogrollModel().query.get(request.args.get('id'))
        data.state = request.args.get('state')
        db.session.add(data)
        db.session.commit()
        flash(f"{data.name}状态修改完成")
        return redirect(url_for('admin.blogroll_list'))
    elif request.args.get('edit') != None:
        if request.method == 'POST':
            db.session.query(blogrollModel).filter(blogrollModel.id == request.args.get('edit')).update(request.form)
            db.session.commit()
            return redirect(url_for('admin.blogroll_list'))
        else:
            data = blogrollModel().query.get(request.args.get('edit'))
            return render_template('admin/blogroll/edit.html',blogroll=data)

    page_size = ConfigModel.query.get(1).number_pages
    search = request.args.get('search')
    if search != None:
        data = blogrollModel.query.filter(blogrollModel.name.like(f'%{search}%')).limit(page_size).limit(page_size).offset((page-1)*page_size).all()
        count = blogrollModel.query.filter(blogrollModel.name.like(f'%{search}%')).count()
        count = len([i+1 for i in range(int(count/page_size))])
    else:
        data = blogrollModel.query.all()
        count = len([i + 1 for i in range(int(len(data) / page_size))])
        search = 0
    return render_template('admin/blogroll/index.html', blogroll=data,count=count,number=search)

# 添加友链
@bp.route('/blogroll/add', methods=['GET', 'POST'])
@admin_login_required
def blogroll_add():
    if request.method == 'POST':
        name = request.form.get('name')
        href = request.form.get('href')
        state = request.form.get('state')
        data = blogrollModel(name=name,href=href,state=state)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('admin.blogroll_list'))
    else:
        return render_template('admin/blogroll/add.html')
