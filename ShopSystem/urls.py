#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 18:28
# @Author  : An ning
# @email   : 18279460212@163.com
# @File    : urls.py
# @Software: PyCharm


from django.urls import path, include

from ShopSystem import views

app_name = 'ShopApp'

urlpatterns = [
    # 给用户增加/减少余额
    path('opebalance/', views.OpeBalance.as_view(), name='opebalance'),

    # 重定向到公众号后端去授权，拿到数据
    path('redirect_wx/', views.RrdirectWechatView.as_view(), name='redirect_wx'),

    # 新增店铺
    path('addshop/', views.AddShopUserView.as_view(), name='addshop'),

    # 新增用户
    path('adduser/', views.AddUserView.as_view(), name='adduser'),

    # 获取店铺营销数据
    path('shop_data/', views.ShopDataView.as_view()),

    # 获取店铺操作员
    path('shopOperator/', views.ShopOperatorView.as_view()),

    # 获取卡的详情
    path('getkainfo/', views.GetKaInfoView.as_view()),

    # 消费详情
    path('expenseinfo/<str:openid>/', views.ExpenseInfoView.as_view(), name='expenseinfo'),
]
