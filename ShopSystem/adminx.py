#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 18:27
# @Author  : An ning
# @email   : 18279460212@163.com
# @File    : adminx.py
# @Software: PyCharm
import requests
import xadmin
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.template import loader
from django.utils.safestring import mark_safe
from xadmin.views import BaseAdminPlugin, ListAdminView, CreateAdminView

from ShopSystem.models import MallShop, UserClass, MallUser, MallService, UserGoods, MallServiceUserGoods, Userbanka, \
    UserExpend, Operator, BillDetail, ActivationCode
from xadmin.layout import Fieldset, Main, Side, Row
from django.utils.translation import ugettext as _
from xadmin import views
from django.utils.encoding import force_text

# 允许所有人删除
from ShopSystem.views import TestView
from shop_manage.base_settings import myreqmaster


class AllowDelete(object):
    def has_delete_permission(self, *args, **kwargs):
        return True


# 不允许任何人删除
class NotAllowDelete(object):
    def has_delete_permission(self, *args, **kwargs):
        return False


@xadmin.sites.register(views.CommAdminView)
class GlobalSetting(object):
    # 改成折叠菜单
    # menu_style = 'accordion'
    # 左上角标题
    site_title = 'Bonina Karrey 美学生活馆'
    # 设置主页页脚
    site_footer = 'Current Editor (2019)'

    # 自定义菜单
    def get_site_menu(self):
        return [
            {
                'title': '店铺营销',
                'icon': 'fa fa-bars',  # Font Awesome图标
                'menus': (
                    {
                        'title': '店铺营销数据',
                        'icon': 'fa fa-bar-chart',
                        'url': "/xadmin/shopdata"

                    },

                )
            },

        ]


xadmin.site.register_view(r'shopdata/$', TestView, name='bug_report')


class AccessLevel:

    def get_model(self):
        return self.model_set

    def queryset(self):
        """改进权限级查看"""
        qs = self.request.user
        shopuser = MallShop.objects.get(username=qs)
        shopuser_root = MallShop.objects.get(username='root')
        if shopuser.is_superuser:
            return self.model._default_manager.get_queryset()
        else:
            return self.get_model().objects.filter(Q(shop=qs) | Q(shop=shopuser_root))
            # return self.get_model().objects.filter(shop=qs)


class ShopUserCreate:
    def save_models(self):
        self.new_obj.shop = self.request.user
        super().save_models()

    # def delete_model(self):
    #     # 删除数据对象
    #     obj = self.obj
    #     print('11111111111111111111111111111111111111111111111111111111')
    #     print(obj)
    #     # 相应的操作
    #     obj.delete()


@xadmin.sites.register(views.BaseAdminView)
class BaseSetting(object):
    # 开启主题切换按钮
    enable_themes = True
    use_bootswatch = True


class MallShopAdmin(NotAllowDelete):
    # 设置显示字段
    list_display = ['show_photo', 'username', 'name', 'province', 'city',
                    'quxian', 'wtchat',
                    'is_staff',
                    'is_active']
    show_detail_fields = ['username']
    show_all_rel_details = True
    # 设置搜索字段
    search_fields = ['username', 'id', 'wtchat', 'name']
    # 设置过滤字段
    list_filter = ['addtime', 'province', 'city', 'quxian', 'is_staff', 'is_active']
    model_icon = 'fa fa-building-o'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("username",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    #  列聚合，可用的值："count","min","max","avg",  "sum"
    # aggregate_fields = {"id": "max"}

    # list页面直接编辑
    list_editable = (
        'province', 'city', 'quxian', 'wtchat', 'is_staff', 'is_active', 'name'
    )
    # 自动刷新
    refresh_times = (3, 5, 10)
    # 添加数据时候，一步一步提供数据
    # wizard_form_list = [
    #     ("基础信息", ("username", "password", "openid", "shop_icon", "infocode")),
    #     ("其它信息", ("last_login", "is_superuser", "name", "province", "city", "quxian", "wtchat")),
    # ]
    # 排序
    ordering = ['-id']
    # 不显示字段
    # exclude = ['addtime']

    # 自读字段
    readonly_fields = ['addtime', 'date_joined', 'last_login']

    # 添加过滤（这里是过滤日期）
    ate_hierarchy = ['addtime']

    #  从‘多选框’的形式改变为‘过滤器’的方式，水平排列过滤器，必须是一个 ManyToManyField类型，且不能用于 ForeignKey字段，默认地，管理工具使用`` 下拉框`` 来展现`` 外键`` 字段
    # filter_horizontal = ('authors',)

    def save_models(self):
        self.new_obj.password = make_password(self.new_obj.password)
        super().save_models()


# 用户级别以及佣金比例表
class UserClassAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    list_display = ['name', 'code', 'money_ratio']
    # 设置搜索字段
    search_fields = ["name"]
    # 设置过滤字段
    list_filter = ['name', 'money_ratio']
    model_icon = 'fa fa-percent'
    show_detail_fields = ['name']
    show_all_rel_details = True
    model_set = UserClass

    # 不显示字段
    exclude = ['shop']
    # 自读字段
    readonly_fields = ['shop']


class MallUserAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['show_photo', 'shop_username', 'level', 'phone', 'money', 'username', 'gender',
                    'over_time_birthday', 'province', 'city',
                    'quxian', 'address', 'wechat', 'age', 'addtime', 'consumption',
                    'satisfaction', 'ope_balance']
    # 设置搜索字段
    search_fields = ['id', 'phone', 'username']
    # 设置过滤字段
    list_filter = ['gender', 'province', 'city', 'quxian', 'birthday', 'age', 'consumption', 'satisfaction']
    model_icon = 'fa fa-users'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("phone",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    #  列聚合，可用的值："count","min","max","avg",  "sum"
    # aggregate_fields = {"id": "max"}
    show_detail_fields = ['phone']
    show_all_rel_details = True
    # list页面直接编辑
    list_editable = (
        'province', 'city', 'quxian', 'wtchat', 'birthday', 'gender', 'username'
    )
    # 自动刷新
    refresh_times = (3, 5, 10)
    # 添加数据时候，一步一步提供数据
    # wizard_form_list = [
    #     ("基础信息", ("username", "password", "openid", "shop_icon", "infocode")),
    #     ("其它信息", ("last_login", "is_superuser", "name", "province", "city", "quxian", "wtchat")),
    # ]
    # 排序
    ordering = ['-consumption']

    # 不显示字段
    exclude = ['shop']

    is_addbalance = True

    # 自读字段
    readonly_fields = ['satisfaction', 'consumption', 'addtime', 'money', 'icon', 'shop']

    # 添加过滤（这里是过滤日期）
    ate_hierarchy = ['addtime']

    model_set = MallUser

    #  从‘多选框’的形式改变为‘过滤器’的方式，水平排列过滤器，必须是一个 ManyToManyField类型，且不能用于 ForeignKey字段，默认地，管理工具使用`` 下拉框`` 来展现`` 外键`` 字段
    # filter_horizontal = ('authors',)

    def shop_username(self, obj):
        return '%s' % obj.shop.name if obj.shop.name else obj.shop.username  # ☆☆☆☆☆

    shop_username.short_description = '店铺'

    # 重写formfield_for_dbfield，设计add和edit表单
    def formfield_for_dbfield(self, db_field, **kwargs):
        if not self.request.user.is_superuser:
            # 对case这个表项的下拉框选择进行过滤

            if db_field.name == "level":
                kwargs["queryset"] = UserClass.objects.filter(shop=self.request.user).order_by('id')

            # if db_field.user_service == "user_service":
            #     kwargs["queryset"] = UserExpend.objects.filter(shop=self.request.user).order_by('id')
            #
            # if db_field.name == "user_service":
            #     kwargs["queryset"] = UserExpend.objects.filter(shop=self.request.user).order_by('id')
            # 对assigned_recipient这个表项的下拉选择进行过滤
            # 并且需要用到外键
            # if db_field.name == "assigned_recipient":
            #     stu_ids = StudentDoctor.objects.filter(doctor=self.request.user).values('student_id')
            #     ids = []
            #     # 这里使用循环，为了下方再次查询时在list中使用in
            #     for id in stu_ids:
            #         ids.append(id['student_id'])
            #     # 根据主键在ids列表中查询得到Queryset。注意kwargs["queryset"]一定是queryset
            #     kwargs["queryset"] = User.objects.filter(pk__in=ids)
            return db_field.formfield(**dict(**kwargs))

        else:
            attrs = self.get_field_attrs(db_field, **kwargs)
            return db_field.formfield(**dict(attrs, **kwargs))


class MallServiceAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['show_icon', 'name', 'introduce', 'money', 'addtime']
    # 设置搜索字段
    search_fields = ['id', 'name']
    # 设置过滤字段
    list_filter = ['money', 'shop', 'addtime']
    model_icon = 'fa fa-star'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("name",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    style_fields = {"content": "ueditor"}
    # 不显示字段
    exclude = ['shop']

    # 自读字段
    readonly_fields = ['shop']
    model_set = MallService


class MallServiceUserGoodsInline(object):
    """会员卡服务项目中间表"""
    model = MallServiceUserGoods
    extra = 0


class UserGoodsAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['name', 'price', 'introduce', 'money', 'past_time', 'addtime', 'usergoods_count']
    show_detail_fields = ['name']
    show_all_rel_details = True
    # 设置搜索字段
    search_fields = ['name', 'id']
    # 设置过滤字段
    list_filter = ['price', 'past_time']
    model_icon = 'fa fa-credit-card'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("name",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    #  列聚合，可用的值："count","min","max","avg",  "sum"
    # aggregate_fields = {"id": "max"}

    # list页面直接编辑
    list_editable = (
        'past_time', 'name', 'price'
    )
    # 自动刷新
    # refresh_times = (3, 5, 10)
    # 添加数据时候，一步一步提供数据
    # wizard_form_list = [
    #     ("基础信息", ("username", "password", "openid", "shop_icon", "infocode")),
    #     ("其它信息", ("last_login", "is_superuser", "name", "province", "city", "quxian", "wtchat")),
    # ]
    # 排序
    ordering = ['-price']

    # 不显示字段
    exclude = ['shop']

    # 自读字段
    readonly_fields = ['shop']

    # 添加过滤（这里是过滤日期）
    ate_hierarchy = ['addtime']

    #  从‘多选框’的形式改变为‘过滤器’的方式，水平排列过滤器，必须是一个 ManyToManyField类型，且不能用于 ForeignKey字段，默认地，管理工具使用`` 下拉框`` 来展现`` 外键`` 字段
    # filter_horizontal = ('MallServiceUserGoods',)

    # 字段显示样式
    # style_fields = {'card_item_configuration': 'm2m_transfer'}
    inlines = [MallServiceUserGoodsInline]

    model_set = UserGoods

    def usergoods_count(self, obj):
        new_obj = MallServiceUserGoods.objects.filter(usergoods=obj)
        data = ''
        for i in new_obj:
            mallservice = i.mallservice
            count = i.count
            data += '<p>' + '服务名称：' + mallservice.name + '&nbsp;&nbsp;&nbsp;' + '次数：' + str(count) + '<p/>'

        return mark_safe(data)  # ☆☆☆☆☆

    usergoods_count.short_description = '卡内项目'


class UserbankaAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['users', 'usergoods_count', 'usergoods', 'money', 'past_time', 'addtime', 'is_past']
    show_detail_fields = ['users']
    show_all_rel_details = True
    # 设置搜索字段
    search_fields = ['users__username', 'id']
    # 设置过滤字段
    list_filter = ['usergoods', 'past_time', 'money']
    model_icon = 'fa fa-id-card'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("users",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    #  列聚合，可用的值："count","min","max","avg",  "sum"
    # aggregate_fields = {"id": "max"}

    # list页面直接编辑
    list_editable = (
        'past_time'
    )
    # 自动刷新
    # refresh_times = (3, 5, 10)
    # 添加数据时候，一步一步提供数据
    # wizard_form_list = [
    #     ("基础信息", ("username", "password", "openid", "shop_icon", "infocode")),
    #     ("其它信息", ("last_login", "is_superuser", "name", "province", "city", "quxian", "wtchat")),
    # ]
    # 排序
    ordering = ['-money']

    # 不显示字段
    exclude = ['shop']

    # 自读字段
    readonly_fields = []

    # 添加过滤（这里是过滤日期）
    ate_hierarchy = ['addtime']

    #  从‘多选框’的形式改变为‘过滤器’的方式，水平排列过滤器，必须是一个 ManyToManyField类型，且不能用于 ForeignKey字段，默认地，管理工具使用`` 下拉框`` 来展现`` 外键`` 字段
    # filter_horizontal = ('MallServiceUserGoods',)

    # 字段显示样式
    # style_fields = {'card_item_configuration': 'm2m_transfer'}

    model_set = Userbanka

    def usergoods_count(self, obj):
        new_obj = MallServiceUserGoods.objects.filter(usergoods=obj.usergoods)
        data = ''
        for i in new_obj:
            number = 0
            userexpend = UserExpend.objects.filter(user_service=i.mallservice, status=False, name=obj.users)
            if userexpend:
                for up in userexpend:
                    if i.usergoods == up.ka.usergoods:
                        number += up.number
            mallservice = i.mallservice
            count = i.count - number
            data += '<p>' + '服务名称：' + mallservice.name + '&nbsp;&nbsp;&nbsp;' + '剩余次数：' + str(count) + '<p/>'

        return mark_safe(data)  # ☆☆☆☆☆

    usergoods_count.short_description = '卡内剩余项目'

    def save_models(self):
        flag = self.org_obj is None and 'create' or 'change'
        if flag == 'create':
            # 卡的价格
            price = self.new_obj.usergoods.price
            self.new_obj.money = self.new_obj.usergoods.money
            """
            办卡返利
            """

            data = requests.get(
                '{}?openid={}'.format(myreqmaster, self.new_obj.users.openid), )
            openid_dict = data.content.decode('utf-8')
            openid = eval(openid_dict).get('openid', '')
            if openid:
                masuser = MallUser.objects.filter(openid=openid).first()
                if masuser:
                    if self.new_obj.users.level:
                        money_ratio = self.new_obj.users.level.money_ratio
                        ratio = price * money_ratio
                        masuser.money += ratio
                        masuser.save()
                        feesource = '【店铺】【{0}】办理会员卡【{1}】，您获得收益【{2}】元'.format(self.new_obj.users, self.new_obj.usergoods,
                                                                             ratio)
                        url = '{}'.format(myreqmaster)
                        data = {
                            'openid': masuser.openid,
                            'msg': feesource
                        }
                        requests.request(method='post', url=url, data=data)
                        remark = "用户【{0}】办理会员卡【{1}】，上级等级为【{2}】，获得的返利【{3}】，店铺收益增加【{4}】元".format(self.new_obj.users,
                                                                                               self.new_obj.usergoods,
                                                                                               self.new_obj.users.level,
                                                                                               ratio,
                                                                                               price - ratio)
                        BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
                    else:
                        remark = "用户【{0}】办理会员卡【{1}】，上级等级为空，无法计算返利，店铺收益增加【{2}】元".format(self.new_obj.users,
                                                                                       self.new_obj.usergoods,
                                                                                       price)
                        BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
                else:
                    remark = "用户【{0}】办理会员卡【{1}】，上级未成为店铺会员，店铺收益增加【{2}】元".format(self.new_obj.users,
                                                                               self.new_obj.usergoods, price)
                    BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
            else:
                remark = "用户【{0}】办理会员卡【{1}】，该用户无上级，店铺收益增加【{2}】元".format(self.new_obj.users, self.new_obj.usergoods,
                                                                        price)
                BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)

        else:
            org_money = self.org_obj.money
            new_money = self.new_obj.money
            if new_money > org_money:
                remark = "用户【{0}】新增会员卡余额【{1}】，店铺收益增加【{2}】元".format(self.new_obj.users, new_money - org_money,
                                                                   new_money - org_money)
                BillDetail.objects.create(money=new_money - org_money, status=True, remark=remark,
                                          shop=self.request.user)
            elif org_money > new_money:
                remark = "用户【{0}】减少会员卡余额【{1}】，店铺收益减少【{2}】元".format(self.new_obj.users, org_money - new_money,
                                                                   org_money - new_money)
                BillDetail.objects.create(money=new_money - org_money, status=False, remark=remark,
                                          shop=self.request.user)
            else:
                pass
        self.new_obj.shop = self.request.user
        super().save_models()

    def formfield_for_dbfield(self, db_field, **kwargs):
        if not self.request.user.is_superuser:
            # 对case这个表项的下拉框选择进行过滤

            if db_field.name == "users":
                kwargs["queryset"] = MallUser.objects.filter(shop=self.request.user).order_by('id')

            if db_field.name == "usergoods":
                kwargs["queryset"] = UserGoods.objects.filter(shop=self.request.user).order_by('id')

            return db_field.formfield(**dict(**kwargs))

        else:
            attrs = self.get_field_attrs(db_field, **kwargs)
            return db_field.formfield(**dict(attrs, **kwargs))


class OperatorAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['name', 'users', 'today_result', 'money', 'satisfaction', 'is_status', 'addtime']
    show_detail_fields = ['users', 'name']
    show_all_rel_details = True
    # 设置搜索字段
    search_fields = ['users__username', 'name']
    # 设置过滤字段
    list_filter = ['is_status', 'satisfaction', 'addtime', 'money']
    model_icon = 'fa fa-free-code-camp'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("name",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    #  列聚合，可用的值："count","min","max","avg",  "sum"
    # aggregate_fields = {"id": "max"}

    # list页面直接编辑
    list_editable = (
        'name',
        'is_status'
    )
    # 自动刷新
    # refresh_times = (3, 5, 10)
    # 添加数据时候，一步一步提供数据
    # wizard_form_list = [
    #     ("基础信息", ("username", "password", "openid", "shop_icon", "infocode")),
    #     ("其它信息", ("last_login", "is_superuser", "name", "province", "city", "quxian", "wtchat")),
    # ]
    # 排序
    ordering = ['-money']

    # 不显示字段
    exclude = ['shop']

    # 自读字段
    readonly_fields = ['service_count', 'shop']

    # 添加过滤（这里是过滤日期）
    ate_hierarchy = ['addtime']

    #  从‘多选框’的形式改变为‘过滤器’的方式，水平排列过滤器，必须是一个 ManyToManyField类型，且不能用于 ForeignKey字段，默认地，管理工具使用`` 下拉框`` 来展现`` 外键`` 字段
    # filter_horizontal = ('MallServiceUserGoods',)

    # 字段显示样式
    # style_fields = {'card_item_configuration': 'm2m_transfer'}

    model_set = Operator

    def today_result(self, obj):
        new_obj = UserExpend.objects.filter(operator=obj)
        number = 0
        count = 0
        grade = 0

        for i in new_obj:
            count += 1
            number += i.number
            grade += i.grade
        if count:
            grade = round(grade / count, 2)
        else:
            grade = 0
        data = '今日项目共 {} 次，今日用户评分为 {} 分'.format(number, grade)
        return data  # ☆☆☆☆☆

    today_result.short_description = '今日业绩'

    def formfield_for_dbfield(self, db_field, **kwargs):
        if not self.request.user.is_superuser:
            # 对case这个表项的下拉框选择进行过滤

            if db_field.name == "users":
                kwargs["queryset"] = MallUser.objects.filter(shop=self.request.user, openid__isnull=True).order_by('id')

            return db_field.formfield(**dict(**kwargs))

        else:
            attrs = self.get_field_attrs(db_field, **kwargs)
            return db_field.formfield(**dict(attrs, **kwargs))


class UserExpendAdmin(AccessLevel, AllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['order_nub', 'user_icon', 'name', 'operator', 'service_name_number', 'xf_time', 'serve_grade',
                    'oper_grade', 'evaluate', 'payment',
                    'status',
                    'ka']
    show_detail_fields = ['order_nub']
    show_all_rel_details = True
    # 设置搜索字段
    search_fields = ['order_nub', 'name__username']
    # 设置过滤字段
    list_filter = ['name', 'operator', 'service_name', 'number', 'xf_time', 'serve_grade', 'oper_grade', 'payment']
    model_icon = 'fa fa-money'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("order_nub",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True
    #  列聚合，可用的值："count","min","max","avg",  "sum"
    # aggregate_fields = {"id": "max"}

    # list页面直接编辑
    list_editable = (
        'operator', 'number', 'payment'
    )
    # 自动刷新
    # refresh_times = (3, 5, 10)
    # 添加数据时候，一步一步提供数据
    # wizard_form_list = [
    #     ("基础信息", ("username", "password", "openid", "shop_icon", "infocode")),
    #     ("其它信息", ("last_login", "is_superuser", "name", "province", "city", "quxian", "wtchat")),
    # ]
    # 排序
    ordering = ['-xf_time']

    # 不显示字段
    exclude = ['shop', 'serve_grade', 'oper_grade', 'evaluate']

    # 自读字段
    readonly_fields = ['service_name', 'order_nub', 'shop']

    # 添加过滤（这里是过滤日期）
    ate_hierarchy = ['xf_time']

    #  从‘多选框’的形式改变为‘过滤器’的方式，水平排列过滤器，必须是一个 ManyToManyField类型，且不能用于 ForeignKey字段，默认地，管理工具使用`` 下拉框`` 来展现`` 外键`` 字段
    # filter_horizontal = ('MallServiceUserGoods',)

    # 字段显示样式
    # style_fields = {'card_item_configuration': 'm2m_transfer'}

    model_set = UserExpend

    is_msg = True

    def service_name_number(self, obj):
        service_name = obj.service_name
        number = obj.number
        data = '<p>' + '服务名称：' + service_name + '&nbsp;&nbsp;&nbsp;' + '次数：' + str(number) + '<p/>'

        return mark_safe(data)  # ☆☆☆☆☆

    service_name_number.short_description = '消费套餐及次数'

    # 重写formfield_for_dbfield，设计add和edit表单
    def formfield_for_dbfield(self, db_field, **kwargs):
        if not self.request.user.is_superuser:
            # 对case这个表项的下拉框选择进行过滤
            if db_field.name == "name":
                kwargs["queryset"] = MallUser.objects.filter(shop=self.request.user).order_by('id')

            if db_field.name == "operator":
                kwargs["queryset"] = Operator.objects.filter(shop=self.request.user).order_by('id')

            if db_field.name == "user_service":
                kwargs["queryset"] = MallService.objects.filter(shop=self.request.user).order_by('id')

            if db_field.name == "ka":
                kwargs["queryset"] = Userbanka.objects.filter(shop=self.request.user).order_by('id')

            return db_field.formfield(**dict(**kwargs))

        else:
            attrs = self.get_field_attrs(db_field, **kwargs)
            return db_field.formfield(**dict(attrs, **kwargs))

    def save_models(self):
        if self.new_obj.user_service:
            self.new_obj.service_name = self.new_obj.user_service.name
        flag = self.org_obj is None and 'create' or 'change'
        if flag == 'create':
            if not self.new_obj.payment:
                userka = Userbanka.objects.filter(users=self.new_obj.name)
                if userka:
                    zhifu = False
                    for i in userka:
                        if i and i.money >= self.new_obj.user_service.money:
                            self.new_obj.status = True
                            self.new_obj.ka = i
                            i.money -= self.new_obj.user_service.money * self.new_obj.number
                            i.save()
                            zhifu = True
                            super().save_models()
                            break
                        else:
                            new_obj = MallServiceUserGoods.objects.filter(usergoods=i.usergoods)
                            for j in new_obj:
                                number = 0
                                userexpend = UserExpend.objects.filter(user_service=j.mallservice, status=False,
                                                                       name=i.users)
                                if userexpend:
                                    for up in userexpend:
                                        if j.usergoods == up.ka.usergoods:
                                            number += up.number
                                mallservice = j.mallservice
                                count = j.count - number
                                if mallservice == self.new_obj.user_service and count and count >= self.new_obj.number:
                                    self.new_obj.status = False
                                    self.new_obj.ka = i
                                    zhifu = True
                                    super().save_models()
                                    break
                    if not zhifu:
                        self.is_msg = False
                        self.message_user(u'卡内余额或套餐次数不足,', 'error')

                else:
                    self.is_msg = False
                    self.message_user(u'请先办卡,', 'error')
            else:
                """
                消费返利
                """
                price = self.new_obj.user_service.money * self.new_obj.number

                # 这里去获取上级
                data = requests.get(
                    '{}?openid={}'.format(myreqmaster, self.new_obj.name.openid), )
                openid_dict = data.content.decode('utf-8')
                openid = eval(openid_dict).get('openid', '')
                if openid:
                    masuser = MallUser.objects.filter(openid=openid).first()
                    if masuser:
                        if self.new_obj.name.level:
                            money_ratio = self.new_obj.name.level.money_ratio
                            ratio = price * money_ratio
                            masuser.money += ratio
                            masuser.save()
                            feesource = '【店铺】【{0}】消费项目【{1}】，您获得收益【{2}】元'.format(self.new_obj.name,
                                                                                self.new_obj.user_service,
                                                                                ratio)
                            url = '{}'.format(myreqmaster)
                            data = {
                                'openid': masuser.openid,
                                'msg': feesource
                            }
                            requests.request(method='post', url=url, data=data)
                            remark = "用户【{0}】消费服务项目【{1}】，上级等级为【{2}】，获得的返利【{3}】，店铺收益增加【{4}】元".format(self.new_obj.name,
                                                                                                    self.new_obj.user_service,
                                                                                                    self.new_obj.name.level,
                                                                                                    ratio,
                                                                                                    price - ratio)
                            BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
                        else:
                            remark = "用户【{0}】消费服务项目【{1}】，上级等级为空，无法计算返利，店铺收益增加【{2}】元".format(self.new_obj.name,
                                                                                            self.new_obj.user_service,
                                                                                            price)
                            BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
                    else:
                        remark = "用户【{0}】消费服务项目【{1}】，上级未成为店铺会员，店铺收益增加【{2}】元".format(self.new_obj.name,
                                                                                    self.new_obj.user_service, price)
                        BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
                else:
                    remark = "用户【{0}】消费服务项目【{1}】，该用户无上级，店铺收益增加【{2}】元".format(self.new_obj.name,
                                                                             self.new_obj.user_service, price)
                    BillDetail.objects.create(money=price, status=True, remark=remark, shop=self.request.user)
                super().save_models()


class BillDetailAdmin(AccessLevel, NotAllowDelete, ShopUserCreate):
    # 设置显示字段
    list_display = ['money', 'status', 'remark', 'sz_time']
    # 设置搜索字段
    search_fields = ['id', 'remark']
    # 设置过滤字段
    list_filter = ['money', 'sz_time', 'status']
    model_icon = 'fa fa-pie-chart'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("money",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True

    # 不显示字段
    exclude = ['shop']

    # is_htmlfile = True
    # 自读字段
    readonly_fields = ['shop']
    model_set = BillDetail
    show_detail_fields = ['money']
    show_all_rel_details = True

    def has_add_permission(self):
        return False

    def has_change_permission(self, obj=None):
        return False

    # data_charts = {
    #     "order_amount": {'title': '店铺年趋势（收支）', "x-field": "sz_time", "y-field": ('money',),
    #                      "order": ('sz_time',)},
    #     # "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
    #     #                 "order": ('create_time',)},
    # }


class ActivationCodeAdmin(AllowDelete):
    # 设置显示字段
    list_display = ['id', 'userinfo', 'verify_code', 'is_use', 'addtime']
    # 设置搜索字段
    search_fields = ['id', 'verify_code']
    # 设置过滤字段
    list_filter = ['is_use', 'addtime']
    model_icon = 'fa fa-pie-chart'
    # list中哪个字段带链接，点击可以进入编辑
    list_display_links = ("verify_code",)
    # 显示还原按钮，删除修改的信息可以还原
    reversion_enable = True

    show_detail_fields = ['verify_code']
    show_all_rel_details = True


from django.contrib.auth import get_user_model  # 获取当前的user_model

xadmin.site.unregister(get_user_model())  # 注销 user
xadmin.site.register(MallShop, MallShopAdmin)  # 注册新的 user
xadmin.site.register(UserClass, UserClassAdmin)
xadmin.site.register(MallUser, MallUserAdmin)
xadmin.site.register(MallService, MallServiceAdmin)
xadmin.site.register(UserGoods, UserGoodsAdmin)
xadmin.site.register(Userbanka, UserbankaAdmin)
xadmin.site.register(Operator, OperatorAdmin)
xadmin.site.register(UserExpend, UserExpendAdmin)
xadmin.site.register(BillDetail, BillDetailAdmin)
xadmin.site.register(ActivationCode, ActivationCodeAdmin)


# —————————————————————————————————————————————— 插件开发 ——————————————————————————————————————————————————————————
# 给用户增加余额
class AddBalance(BaseAdminPlugin):
    """给用户增加余额"""
    # 默认不加载，只在需要加载的options中设置True来加载
    is_addbalance = False

    def init_request(self, *arg, **kwargs):
        return self.is_addbalance

    def get_media(self, media):
        # 此处用来加入我们自己的js文件

        media = media + self.vendor("xadmin.self.addbalance.js")
        return media


xadmin.site.register_plugin(AddBalance, ListAdminView)


# 测试html插件
class htmlfile(BaseAdminPlugin):
    """给用户增加余额"""
    # 默认不加载，只在需要加载的options中设置True来加载
    is_htmlfile = False

    def init_request(self, *args, **kwargs):  # 指定特定页面显示插件
        return bool(self.is_htmlfile)

    # toolbar中插件显示页面
    def block_nav_form(self, context, nodes):
        if self.is_htmlfile:
            nodes.append(
                loader.render_to_string('xadmin/htmlfile1.html'),
                # context_instance=context
            )

    def get_media(self, media):
        # 此处用来加入我们自己的js文件

        media = media + self.vendor("xadmin.self.htmlfile1.js")
        return media


xadmin.site.register_plugin(htmlfile, ListAdminView)
