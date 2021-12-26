from datetime import datetime

from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
import sys
sys.path.append('..')
from Model import articleModel,NavModel,ConfigModel
from extension import db,and_
bp = Blueprint('index',__name__,url_prefix='/')

@bp.route('/')
def index():
    data = articleModel.query.order_by(articleModel.datetime.desc()).all()[:ConfigModel.query.get(1).number_pages]
    datas = articleModel.query.order_by(articleModel.Access_number.desc()).all()[:ConfigModel.query.get(1).number_pages]
    articles = articleModel.query.limit(9).all()
    return render_template('index/index/index.html',articles=articles,data=data,datas=datas)

# 404
@bp.errorhandler(404)
def errorhandler(error):
    return render_template('error/404.html'),404

# 获取目录
@bp.route('/<address>')
def get_address(address):
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    if ConfigModel.query.get(1) == None:
        config = ConfigModel(id=1,number_pages=8,name="开心小窝")
        db.session.add(config)
        db.session.commit()
    nav_id = criteria_href(address)
    if nav_id == "":
        return abort(404)
    elif NavModel().query.get(nav_id).state != 1:
        return abort(404)
    name = NavModel().query.get(nav_id)
    name = name.nav_name
    page_size = ConfigModel.query.get(1).number_pages

    data = articleModel.query.order_by(articleModel.datetime.desc()).all()[:ConfigModel.query.get(1).number_pages]
    datas = articleModel.query.order_by(articleModel.Access_number.desc()).all()[:ConfigModel.query.get(1).number_pages]

    count = articleModel.query.filter(articleModel.nav_bar_id == nav_id).count()
    count = len([i+1 for i in range(int(count/page_size))])
    article = articleModel.query.filter(articleModel.nav_bar_id == nav_id).limit(page_size).offset((page-1)*page_size).all()
    return render_template('index/article/index.html',articles=article,name=name,count=count,number=page,data=data,datas=datas)

# 获取子地址
@bp.route('/<address>/<subaddress>',methods=['GET','POST'])
def get_subaddress(address,subaddress):
    nav_id = criteria_href(address)
    if nav_id == "":
        return abort(404)
    subdate = articleModel.query.filter(and_(articleModel.id == subaddress,articleModel.nav_bar_id == nav_id)).first()
    if subdate == None:
        return abort(404)
    elif NavModel().query.get(nav_id).state != 1:
        return abort(404)
    befores = articleModel.query.filter(articleModel.id == int(subaddress) - 1).first()
    if befores == None:
        befores = articleModel.query.filter(articleModel.id == subaddress).first()
    ends = articleModel.query.filter(articleModel.id == int(subaddress) + 1).first()
    data = articleModel.query.order_by(articleModel.datetime.desc()).all()[:ConfigModel.query.get(1).number_pages]
    datas = articleModel.query.order_by(articleModel.Access_number.desc()).all()[:ConfigModel.query.get(1).number_pages]


    if ends == None:
        ends = articleModel.query.filter(articleModel.id == subaddress).first()
    if request.method == 'POST':
        if request.form.get('password') != subdate.encryption_code:
            flash('密码错误')
            return redirect(url_for('index.get_subaddress', address=address, subaddress=subaddress))
        article_encryption = True
        return render_template('index/article/article.html', subdate=subdate, article_encryption=article_encryption,ends=ends,befores=befores,data=data,datas=datas)
    else:
        subdate.Access_number = subdate.Access_number + 1
        db.session.add(subdate)
        db.session.commit()
        article_encryption = False

        return render_template('index/article/article.html',subdate=subdate,article_encryption=article_encryption,ends=ends,befores=befores,data=data,datas=datas)


@bp.route('/search')
def search():
    name = request.args.get('content')
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    count = articleModel.query.filter(articleModel.article_title.like(f'%{name}%')).count()
    page_size = ConfigModel.query.get(1).number_pages
    count = len([i + 1 for i in range(int(count / page_size))])+1
    article = articleModel.query.filter(articleModel.article_title.like(f'%{name}%')).limit(page_size).offset(
        (page - 1) * page_size).all()
    return render_template('index/search/index.html', articles=article, name=name, count=count, number=page)

# 判断地址是否合规
def criteria_href(address):
    address = "/" + address
    nav = NavModel().query.all()
    res = False
    id = ""
    for i in nav:
        if address == i.nav_href:
            id = i.id
            res = True
            break
    if res == False:
        return ""
    return id