from django.db import models

# Create your models here.

import random
import time
import datetime
from DjangoUeditor.models import UEditorField
from django.db import models
from django.utils.safestring import mark_safe
# Create your models here.
from django.contrib.auth.models import AbstractUser

# 店铺表
from xadmin.models import Log


class MallShop(AbstractUser):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='店铺名')
    openid = models.CharField(max_length=255, verbose_name='openid')
    shop_icon = models.CharField(max_length=255, blank=True, verbose_name='店铺头像')
    infocode = models.CharField(max_length=255, blank=True, verbose_name='激活码')
    province = models.CharField(max_length=30, blank=True, null=True, verbose_name='省份')
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name='城市')
    quxian = models.CharField(max_length=30, blank=True, null=True, verbose_name='区县')
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name='地址')
    wtchat = models.CharField(max_length=30, blank=True, null=True, verbose_name='微信')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='激活时间')
    qrcode = models.ImageField(upload_to='shop/qrcode/', blank=True, editable=False, verbose_name='二维码',
                               help_text='用户扫码即可成为店铺会员')

    def show_photo(self):
        text = """<img src="%s" style="width:50px;"/>""" % self.shop_icon if self.shop_icon else ''
        return mark_safe(text)

    show_photo.short_description = '店铺头像'

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'MallShop'
        verbose_name = "店铺表"
        verbose_name_plural = verbose_name


# 用户级别以及佣金比例表
class UserClass(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='级别编号', help_text='最低级别为 1，每高一级，级别编号 + 1')
    name = models.CharField(max_length=20, verbose_name='级别昵称')
    money_ratio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='返利比例')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'UserClass'
        verbose_name = "级别设置"
        verbose_name_plural = verbose_name


# 用户管理
class MallUser(models.Model):
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')
    level = models.ForeignKey(to='UserClass', on_delete=models.PROTECT, blank=True, null=True, verbose_name='用户级别')
    openid = models.CharField(max_length=255, unique=True, verbose_name='openid')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号')
    username = models.CharField(max_length=50, default='匿名用户', verbose_name='用户名')
    icon = models.CharField(max_length=255, blank=True, verbose_name='头像')
    gender = models.NullBooleanField(default=None, verbose_name='性别', choices=((None, '不详'), (True, '男'), (False, '女')))
    province = models.CharField(max_length=30, blank=True, null=True, verbose_name='省份')
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name='城市')
    quxian = models.CharField(max_length=30, blank=True, null=True, verbose_name='区县')
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name='地址')
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='余额')
    wechat = models.CharField(max_length=100, blank=True, verbose_name='微信')
    birthday = models.DateTimeField(default=None, blank=True, null=True, verbose_name='生日')
    age = models.CharField(blank=True, max_length=15, verbose_name='年龄')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    consumption = models.IntegerField(default=0, verbose_name='消费指数', help_text='平均没人每月来的次数，大于5则高于平均指数，小于则低于平均指数')
    satisfaction = models.IntegerField(default=0, verbose_name='满意度', help_text='根据用户对服务的评价，5为最高，0为最低')
    qrcode = models.ImageField(upload_to='user/qrcode/', blank=True, editable=False, verbose_name='二维码',
                               help_text='用户扫码即可成为店铺会员')

    def show_photo(self):
        """按行显示出货详情"""
        text = """<img src="%s" style="width:50px;"/>""" % self.icon if self.icon else ''
        return mark_safe(text)

    show_photo.short_description = '用户头像'

    def over_time_birthday(self):
        if self.birthday:
            month = now.month - self.birthday.month
            day = now.day - self.birthday.day
            if not month:
                text = "<p style='color:red'>会员还剩{}天生日<p/>".format(day)
            else:
                text = "<p style='color:red'>会员还剩{}月{}天生日<p/>".format(month, day)
            return mark_safe(text)
        else:
            return mark_safe("")

    over_time_birthday.short_description = '会员生日'

    def ope_balance(self):
        """给用户添加佣金，发送通知"""
        if self.openid:
            text = """<input type="button" value="增加余额" userid="{0}" class="addbalance" />
                      <input type="button" value="扣除余额" userid="{1}" class="subbalance" />
                    """.format(self.id, self.id)
        else:
            text = ""
        return mark_safe(text)

    ope_balance.short_description = '余额操作'

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'MallUser'
        verbose_name = "用户管理"
        verbose_name_plural = verbose_name
        ordering = ['-addtime']


# 服务项目
class MallService(models.Model):
    icon = models.ImageField(upload_to='service/icon/', verbose_name='图片')
    name = models.CharField(max_length=100, verbose_name='服务名称')
    introduce = models.TextField(blank=True, verbose_name='服务介绍')
    content = UEditorField(verbose_name="服务详情", imagePath="service/images/", filePath="service/files/", blank=True)
    money = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='服务价格')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='增加时间')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')  # 创建该数据的登录用户

    def show_icon(self):
        """按行显示出货详情"""
        text = """<img src="%s" style="width:50px;"/>""" % self.icon.url if self.icon else ''
        return mark_safe(text)

    show_icon.short_description = '项目图片'

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'MallService'
        verbose_name = "服务项目"
        verbose_name_plural = verbose_name


# 会员卡设置
class UserGoods(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True, verbose_name='会员卡昵称')
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='会员卡价格')
    introduce = models.TextField(blank=True, verbose_name='会员卡介绍')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    past_time = models.DateTimeField(verbose_name='过期时间')
    money = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='余额', help_text='设置卡内余额')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')  # 创建该数据的登录用户
    card_item_configuration = models.ManyToManyField(MallService, through='MallServiceUserGoods',
                                                     through_fields=('usergoods', 'mallservice'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'UserGoods'
        verbose_name = "会员卡设置"
        verbose_name_plural = verbose_name


# 会员卡服务项目中间表
class MallServiceUserGoods(models.Model):
    usergoods = models.ForeignKey(to='UserGoods', on_delete=models.PROTECT)
    mallservice = models.ForeignKey(to='MallService', on_delete=models.PROTECT, verbose_name='服务名称')
    count = models.SmallIntegerField(default=1, verbose_name='次数')

    class Meta:
        db_table = 'MallServiceUserGoods'
        verbose_name = "会员卡服务项目中间表"
        verbose_name_plural = verbose_name


now = datetime.datetime.now()


# 会员卡管理
class Userbanka(models.Model):
    users = models.ForeignKey(to='MallUser', on_delete=models.PROTECT, verbose_name='用户名')
    usergoods = models.ForeignKey(to='UserGoods', on_delete=models.PROTECT, verbose_name='会员卡昵称')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    past_time = models.IntegerField(default=1, verbose_name='过期时间（天）', help_text='设置卡的有效期，从生成卡开始，单位为天')
    money = models.DecimalField(max_digits=20, decimal_places=2, default=0, editable=False, verbose_name='余额')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')  # 创建该数据的登录用户

    def is_past(self):
        count_time = now > self.addtime + datetime.timedelta(days=self.past_time)
        if count_time:
            text = "<p style='color:red'>已过期<p/>"
        else:
            over_day = (self.addtime + datetime.timedelta(days=self.past_time)) - now
            text = "<p style='color:green'>正常`剩余时间：{}天<p/>".format(over_day.days)
        return mark_safe(text)

    is_past.short_description = '会员卡状态'

    def over_past_time(self):
        over_day = (self.addtime + datetime.timedelta(days=self.past_time)) - now
        return over_day.days if over_day.days > 0 else 0

    def __str__(self):
        # return self.usergoods.name
        return self.usergoods.name if self.usergoods.name else self.users.username

    class Meta:
        db_table = 'Userbanka'
        verbose_name = "会员卡管理"
        verbose_name_plural = verbose_name


# 员工设置
class Operator(models.Model):
    name = models.CharField(max_length=30, verbose_name='员工昵称')
    users = models.ForeignKey(to='MallUser', on_delete=models.PROTECT, verbose_name='用户名')
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='总业绩')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    satisfaction = models.IntegerField(default=0, verbose_name='满意度', help_text='根据用户对服务的评价，5为最高，0为最低')
    service_count = models.SmallIntegerField(default=0, verbose_name='服务总数', help_text='服务用户的总数量')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')  # 创建该数据的登录用户
    is_status = models.NullBooleanField(default=None, choices=((None, '下班'), (False, '离职'), (True, '上班中')),
                                        verbose_name='职员状态')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Operator'
        verbose_name = '员工管理'
        verbose_name_plural = verbose_name


def uuid():
    local_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))[2:]
    result = local_time + str(random.randint(1000, 9999))
    return result


# 用户消费管理
class UserExpend(models.Model):
    order_nub = models.CharField(default=uuid, max_length=50, verbose_name='订单号')
    name = models.ForeignKey(to='MallUser', on_delete=models.PROTECT, verbose_name='顾客')
    operator = models.ForeignKey(to='Operator', on_delete=models.PROTECT, verbose_name='操作员工')
    user_service = models.ForeignKey(to='MallService', on_delete=models.PROTECT, verbose_name='服务名称')
    service_name = models.CharField(max_length=100, verbose_name='服务名称')
    number = models.SmallIntegerField(default=1, verbose_name='次数')
    xf_time = models.DateTimeField(auto_now_add=True, verbose_name='消费时间')
    grade = models.SmallIntegerField(default=5, verbose_name='评分')
    evaluate = models.TextField(blank=True, verbose_name='评价')
    status = models.NullBooleanField(default=None, choices=((None, ''), (False, '扣次'), (True, '扣余额')), editable=False,
                                     verbose_name='会员卡详情')
    payment = models.BooleanField(default=False, choices=((False, '会员卡'), (True, '现金支付')), verbose_name='支付方式')
    ka = models.ForeignKey(to='Userbanka', on_delete=models.SET_NULL, blank=True, editable=False, null=True,
                           verbose_name='会员卡')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')  # 创建该数据的登录用户

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'UserExpend'
        verbose_name = '消费管理'
        verbose_name_plural = verbose_name


# 手机验证码管理表
class AuthCode(models.Model):
    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    purpose = models.IntegerField(default=0, verbose_name='用途', help_text=':0->注册验证 1->登录 2->绑定手机 3->找回密码 4->其它')
    creation_time = models.DateTimeField(auto_now=True, verbose_name='发送时间')

    class Meta:
        db_table = 'phone_authCode'
        verbose_name = '手机验证码'
        verbose_name_plural = verbose_name


# 店铺流水详情
class BillDetail(models.Model):
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='金额')
    shop = models.ForeignKey(to='MallShop', on_delete=models.PROTECT, editable=False, verbose_name='所属店铺')  # 创建该数据的登录用户
    sz_time = models.DateTimeField(auto_now_add=True, verbose_name='收支时间')
    status = models.BooleanField(default=True, choices=((True, '收入'), (False, '支出')), verbose_name='类型')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        db_table = 'bill_detail'
        verbose_name = '账单流水明细'
        verbose_name_plural = verbose_name


# 激活码
class ActivationCode(models.Model):
    verify_code = models.CharField(max_length=255, verbose_name='激活码')
    is_use = models.BooleanField(default=False, verbose_name='是否使用')
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='激活时间')

    def userinfo(self):
        text = ""
        if self.is_use:
            shopuser = MallShop.objects.filter(infocode=self.verify_code)
            if shopuser:
                for shop in shopuser:
                    text = '<p style="color:green">{1}<p/><img src="{0}" style="width:50px;"/>'.format(
                        shop.shop_icon, shop.username)
        return mark_safe(text)

    userinfo.short_description = '店铺昵称头像'

    class Meta:
        db_table = 'ActivationCode'
        verbose_name = '激活码'
        verbose_name_plural = verbose_name
