from flask import Flask,g
from flask_migrate import Migrate
from extension import db
from view.index import index_bp
from view.admin import admin_bp
from Model import ConfigModel,NavModel,blogrollModel
import config

app = Flask(__name__)


# 加载配置函数
app.config.from_object(config)
# 加载数据库
db.init_app(app)

# 注册迁移脚本
migrate = Migrate(app,db)

# 注册蓝图
app.register_blueprint(index_bp)

# 后端
app.register_blueprint(admin_bp)

@app.before_request
def before_request():
    # 获取网站配置信息
    g.config = ConfigModel.query.get(1)
    # 获取导航条
    g.navigation_bar = NavModel.query.all()
    # 获取友情链接
    g.blogroll = blogrollModel().query.all()



if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0')