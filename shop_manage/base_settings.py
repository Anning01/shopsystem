# -*- coding: utf-8 -*-
# 配置数据库
import redis as redis

DATANASE_HOST = '127.0.0.1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 修改数据库为MySQL，并进行配置
        'NAME': 'ShopSystem',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': DATANASE_HOST,
        'PORT': 3306,
        'OPTIONS': {'charset': 'utf8mb4', }
    }
}
#
# AUTHENTICATION_BACKENDS = (
#     'rules.permissions.ObjectPermissionBackend',
#     'django.contrib.auth.backends.ModelBackend',
# )

# redis_client = redis.Redis(
#     host=DATANASE_HOST,
#     port=6379,
#     db=0,
#     password='sailafeina'
# )

# 网站默认设置和上下文信息
SITE_END_TITLE = ''  # 网站的名称
SITE_DESCRIPTION = ''  # 描述
SITE_KEYWORDS = ''


AUTH_USER_MODEL = 'ShopSystem.MallShop'

# ------------------------邮箱配置-----------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 把要发送的邮件显示再控制台上，方便调试
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.163.com'  # 如果是 163 改成 smtp.163.com
EMAIL_PORT = 465
EMAIL_HOST_USER = ''  # 帐号
EMAIL_HOST_PASSWORD = ''  # 到邮箱里开通
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ---------------------------------------------------oss设置------------------------------------------------------------ #

OSS_INTERIOR_WEB_URL = ''
ACCESS_KEY_ID = ""
ACCESS_KEY_SECRET = ""
END_POINT = "oss-cn-shenzhen.aliyuncs.com"
PREFIX_URL = 'https://'
BUCKET_NAME = ""
ALIYUN_OSS_CNAME = ""  # 自定义域名，如果不需要可以不填写
BUCKET_ACL_TYPE = "public-read"  # private, public-read, public-read-write
DEFAULT_FILE_STORAGE = 'aliyun_oss2_storage.backends.AliyunMediaStorage'
MEDIA_URL = ''
# MEDIA_ROOT = "media"

# ---------------------------------------------------oss设置------------------------------------------------------------ #


# WEB_URL = 'https://media.sailafeinav.com'
WEB_URL = PREFIX_URL + OSS_INTERIOR_WEB_URL
"""富文本配置"""
UEDITOR_SETTINGS = {
    "config": {

    },
    "upload": {
        "imageUrlPrefix": ALIYUN_OSS_CNAME,
        "videoUrlPrefix": ALIYUN_OSS_CNAME,
        "fileUrlPrefix": ALIYUN_OSS_CNAME,
    }
}
RUL_MEDIA_ROOT = ALIYUN_OSS_CNAME + MEDIA_URL
EGP_MEDIA_ROOT = WEB_URL + MEDIA_URL


# 重定向的域名 我自己和我公众号交互
mygzhurl = ''