
# 数据库配置
HOST = 'rm-bp1r040zygb637095co.mysql.rds.aliyuncs.com' # 地址
PORT = 3306 # 数据库端口
USERNAME = 'time' # 数据库用户名
PASSWORLD = 'Abcd1234' # 数据库密码
DATBASE = 'blog' # 数据库名
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORLD,HOST,PORT,DATBASE)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = True

# 配置seession KEY
SECRET_KEY = 'AFHJKLFMKLAKJFGOQahanjkfbla113891434h1kj34g1i3u4h7813hir'

# 设置缓存时长
SEND_FILE_MAX_AGE_DEFAULT = 3600