import datetime
import decimal
import json
import os
import uuid

import oss2
import requests
from django.db.models.aggregates import Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
import qrcode as qrcode
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from xadmin.views import CommAdminView
from django.contrib.auth.models import Group
from ShopSystem.models import MallUser, MallShop, BillDetail, Userbanka, Operator, ActivationCode, MallServiceUserGoods, \
    UserExpend
from shop_manage.base_settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, BUCKET_NAME, mygzhurl
from django.views.decorators.csrf import csrf_exempt


def bad_request(request):
    return render(request, '400.html')


def page_not_found(request):
    return render(request, '404.html')


def page_error(request):
    return render(request, '500.html')


class OpeBalance(APIView):
    """给用户增加余额"""

    def post(self, request, *args, **kwargs):
        ope_user = request.POST.get('ope_user', '')  # 操作人
        userid = request.POST.get('userid', '')  # 用户编号
        fee = request.POST.get('fee', '')  # 金额
        get_type = request.POST.get('type', '')  # 操作类型
        http_referer = request.META.get('HTTP_REFERER', '')
        if 'xadmin' not in http_referer:  # 安全拦截
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        # 佣金来源说明
        feesource = request.POST.get('desc', '')

        if '' in [ope_user, userid, fee, get_type] or get_type not in ['add', 'sub']:
            return Response({'code': 1, 'msg': 'error'})
        try:
            fee = round(decimal.Decimal(fee), 2)
        except:
            return Response({'code': 1, 'msg': 'error'})

        user = MallUser.objects.filter(id=userid).first()
        if not user:
            return Response({'code': 1, 'msg': '用户不存在'})
        shop_query = MallShop.objects.filter(username=ope_user).first()
        if not shop_query:
            shop_name = ope_user
        else:
            shop_name = shop_query.name if shop_query.name else shop_query.username
        if get_type == 'add':
            feesource_ca = '【店铺】【{0}】给你增加余额【{1}】元，请查收！'.format(shop_name, fee)
            # 给用户增加余额
            user.money += fee  # 给用户增加余额
            user.save()
            # 增加支出明细
            BillDetail.objects.create(money=fee, shop=shop_query, status=False, remark=feesource)
        else:
            feesource_ca = '【店铺】【{0}】扣除你的余额【{1}】元'.format(ope_user, fee)
            # 给用户扣除余额
            user.balance -= fee  # 给用户扣除余额
            user.save()
            # 增加支出明细
            BillDetail.objects.create(money=fee, shop=shop_query, status=True, remark=feesource)

        # TODO 发到用户的公众号给用户发送信息
        feesource += feesource_ca
        url = mygzhurl
        data = {
            'openid': user.openid,
            'msg': feesource
        }
        requests.request(method='post', url=url, data=data)
        return Response({'code': 0, 'msg': '操作成功'})


from django.contrib.auth.hashers import make_password


class AddUserView(APIView):
    def get(self, req, *args, **kwargs):
        username = req.GET.get('username', '')
        password = req.GET.get('password', '')
        openid = req.GET.get('openid', '')
        infocode = req.GET.get('infocode', '')
        password = make_password(password)
        a = MallShop.objects.create(username=username, password=password, openid=openid, infocode=infocode)
        data = {
            'username': a.username,
            'password': a.password,
            'openid': a.openid,
            'infocode': a.infocode,
        }
        return Response(data)

    def post(self, req, *args, **kwargs):

        openid = req.POST.get('openid', '')
        if not openid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 手机号
        phone = req.POST.get('phone', '')
        # 省
        province = req.POST.get('province', '')

        # 市
        city = req.POST.get('city', '')

        # 区县
        quxian = req.POST.get('quxian', '')

        # 地址
        address = req.POST.get('address', '')

        # 微信
        wechat = req.POST.get('wechat', '')

        if phone:
            # 年龄
            age = req.POST.get('age', '')

            # 生日
            birthday = req.POST.get('birthday', '')
            try:
                user = MallUser.objects.get(openid=openid)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.phone = phone
            user.province = province
            user.city = city
            user.quxian = quxian
            user.address = address
            user.wechat = wechat
            user.age = age
            user.birthday = datetime.datetime.strptime(birthday.replace('/', '-'), '%Y-%m-%d')
            user.save()
            userka = Userbanka.objects.filter(users=user)
            return render(req, 'index.html', context={'context': user, 'userka': userka})
        else:
            # 邮箱
            email = req.POST.get('email', '')
            # 激活码
            infocode = req.POST.get('infocode', '')

            code = ActivationCode.objects.filter(verify_code=infocode, is_use=False)
            if not code:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            code.update(is_use=True)
            # 店铺昵称
            name = req.POST.get('name', '')
            try:
                user = MallShop.objects.get(openid=openid)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.province = province
            user.city = city
            user.quxian = quxian
            user.address = address
            user.wechat = wechat
            user.email = email
            user.infocode = infocode
            user.name = name
            user.is_staff = True
            user.save()

            return HttpResponseRedirect('/xadmin/')


class ShopDataView(APIView):

    def get(self, req, *args, **kwargs):
        # 日收益，周收益，月收益，日增长人数，周增长人数，月增长人数，卡内余额总数，店铺总收益，店铺总支出

        shop_id = req.GET.get('shop_id', '')

        if not shop_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            shop = MallShop.objects.get(username=shop_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        now = datetime.datetime.now()

        shop_month_data = BillDetail.objects.filter(shop=shop, sz_time__gte=datetime.date(now.year, now.month, 1))
        MallUser_month_data = MallUser.objects.filter(shop=shop, addtime__gte=datetime.date(now.year, now.month, 1))

        earnings_day, earnings_week, earnings_month = 0, 0, 0
        for i in shop_month_data:
            if i.status:
                if i.sz_time >= datetime.datetime(now.year, now.month, now.day):
                    earnings_day += i.money
                if i.sz_time >= datetime.datetime(now.year, now.month, now.day - now.weekday()):
                    earnings_week += i.money
                    earnings_month += i.money

        user_day, user_week, user_month = 0, 0, 0
        for i in MallUser_month_data:
            if i.addtime >= datetime.datetime(now.year, now.month, now.day):
                user_day += 1
            if i.addtime >= datetime.datetime(now.year, now.month, now.day - now.weekday()):
                user_week += 1
            user_month += 1
        calallmoney = Userbanka.objects.all().aggregate(nums=Sum('money'))
        shop_income = BillDetail.objects.filter(status=True).aggregate(nums=Sum('money'))
        shop_expend = BillDetail.objects.filter(status=False).aggregate(nums=Sum('money'))
        data = {
                   'name': '店铺总收益',
                   'data': round(shop_income['nums'], 2) if shop_income['nums'] else 0, }, {

                   'name': '店铺总支出',
                   'data': round(shop_expend['nums'], 2) if shop_expend['nums'] else 0, }, {

                   'name': '卡内余额总数',
                   'data': round(calallmoney['nums'], 2) if calallmoney['nums'] else 0, }, {

                   'name': '店铺日收益',
                   'data': round(earnings_day, 2), }, {

                   'name': '店铺周收益',
                   'data': round(earnings_week, 2), }, {

                   'name': '店铺月收益',
                   'data': round(earnings_month, 2), }, {

                   'name': '店铺日增长人数',
                   'data': user_day, }, {

                   'name': '店铺周增长人数',
                   'data': user_week, }, {

                   'name': '店铺月增长人数',
                   'data': user_month, }
        return Response(data)

    def post(self, req, *args, **kwargs):
        # 店铺每月数据收支表，每月人数增长表

        shop_id = req.POST.get('shop_id', '')

        if not shop_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            shop = MallShop.objects.get(username=shop_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        now = datetime.datetime.now()

        year = now.year
        month = now.month
        day = now.day
        billset = BillDetail.objects.filter(shop=shop, sz_time__gte=datetime.datetime(year - 1, month, day))
        userset = MallUser.objects.filter(shop=shop, addtime__gte=datetime.datetime(year - 1, month, day))
        data = []
        year -= 1
        month += 1
        for i in range(1, 13):
            income = billset.filter(sz_time__year=year, sz_time__month=month, status=True).aggregate(
                nums=Sum('money'))
            expend = billset.filter(sz_time__year=year, sz_time__month=month, status=False).aggregate(
                nums=Sum('money'))
            user_number = userset.filter(addtime__year=year, addtime__month=month).count()
            data.append({'{}-{}'.format(year, month): [
                {'收入数据': income['nums'] if income['nums'] else 0, '支出数据': expend['nums'] if expend['nums'] else 0,
                 '用户数据': user_number}]})
            month += 1
            if month > 12:
                year += 1
                month = 1

        return Response(data)


class TestView(CommAdminView):
    def get(self, request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据
        title = "店铺营销数据"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        return render(request, 'xadmin/htmlfile1.html', context)  # 最后指定自定义的template模板，并返回context


# 生成二维码
def UserQRcode(user_qrcode, shopid, data_type):
    paths = user_qrcode
    img = qrcode.make(paths)
    name = uuid.uuid4()
    img.save('{}.jpg'.format(name))

    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)  # 登陆阿里云oss服务
    bucket = oss2.Bucket(auth, "oss-cn-shenzhen-internal.aliyuncs.com",
                         BUCKET_NAME)  # 第二个参数一定要写EndPoint（地域节点）,不能写Bucket 域名
    if data_type:
        MallUser.objects.filter(id=shopid).update(qrcode='user/qrcode/{}.jpg'.format(name))
    else:
        MallShop.objects.filter(id=shopid).update(qrcode='user/qrcode/{}.jpg'.format(name))
    bucket.put_object_from_file('user/qrcode/{}.jpg'.format(name), '{}.jpg'.format(name))

    os.remove('{}.jpg'.format(name))


class AddShopUserView(APIView):
    """
    get:返回首页或者注册页面，店铺用户重定向到xadmin
    post:接收公众号后台发送过来的用户和店铺数据
    """

    def get(self, req, *args, **kwargs):
        openid = req.GET.get('openid', '')
        request_type = req.GET.get('type', '')
        if request_type == 'user':
            if not openid:
                return HttpResponseRedirect('/redirect_wx/?type=user')
            context = MallUser.objects.filter(openid=openid).first()
            if not context:
                return HttpResponseRedirect('/redirect_wx/?type=user')
            if context.phone:
                userka = Userbanka.objects.filter(users=context)
                return render(req, 'index.html', context={'context': context, 'userka': userka})
            else:
                return render(req, 'register.html', context={'context': context})
        elif request_type == 'shop':
            if not openid:
                return HttpResponseRedirect('/redirect_wx/?type=shop')
            context = MallShop.objects.filter(openid=openid).first()
            if not context:
                return HttpResponseRedirect('/redirect_wx/?type=shop')
            if context.email:
                return HttpResponseRedirect('/xadmin/')
            else:

                return render(req, 'shop_register.html', context={'context': context})
        return HttpResponseRedirect('/redirect_wx/?type=user')

    def post(self, req, *args, **kwargs):
        """
        接收公众号后台发送过来的用户和店铺数据
        :param req:
        :param args:
        :param kwargs:
        :return:
        """
        data_type = req.POST.get('data_type', '')
        if not data_type:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        nickname = req.POST.get('nickname', '')
        icon = req.POST.get('icon', '')
        openid = req.POST.get('openid', '')
        province = req.POST.get('province', '')
        city = req.POST.get('city', '')
        quxian = req.POST.get('quxian', '')
        gender = req.POST.get('gender', '')
        address = req.POST.get('address', '')

        if data_type == 'shop':
            phone = req.POST.get('phone', '')
            if not phone:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            is_shop_user = MallShop.objects.filter(username=phone)
            if is_shop_user:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            group = Group.objects.filter(id=1).first()

            brand_name = '店铺统一昵称'  # 店铺统一昵称

            shop = MallShop(username=phone)
            shop.password = make_password(phone)
            shop.is_superuser = False
            shop.first_name = phone
            if nickname:
                shop.last_name = nickname
                shop.name = nickname
            if icon:
                shop.shop_icon = icon
            if openid:
                shop.openid = openid
            if province:
                shop.province = province
            if city:
                shop.city = city
            if quxian:
                shop.province = quxian

            shop.save()
            shop.name = '{}'.format(brand_name + str(shop.id) + '号店铺')

            UserQRcode("{}?type={}&shop={}&openid={}".format(mygzhurl, 'user',
                                                                                                       shop.username,
                                                                                                       shop.openid),
                       shop.id, 0)
            if not group:
                group = Group.objects.first()
            shop.groups.add(group)
            return Response({'code': 0, 'Message': '新增店铺成功', 'result': ''})

        elif data_type == 'user':
            shop_name = req.POST.get('shop', '')
            shop = MallShop.objects.filter(username=shop_name)
            if not shop_name or not openid or not shop:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            is_user = MallUser.objects.filter(openid=openid)
            if is_user:
                return Response({'code': 1, 'Message': '用户已存在', 'result': ''})
            user = MallUser()
            user.shop = shop.first()
            user.openid = openid

            if nickname:
                user.username = nickname
            if icon:
                user.icon = icon
            if gender:
                user.gender = gender

            if province:
                user.province = province
            if city:
                user.city = city
            if quxian:
                user.quxian = quxian
            if address:
                user.address = address
            user.save()
            UserQRcode("{}?code={}&shop={}&openid={}".format(mygzhurl, data_type,
                                                                                                       shop.first().username,
                                                                                                       user.openid),
                       user.id, 1)
            return Response({'code': 0, 'Message': '新增用户成功', 'result': ''})
        return Response(status=status.HTTP_400_BAD_REQUEST)


def ValidateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class RrdirectWechatView(APIView):
    """
    get:重定向到微信后台去授权
    """

    def get(self, req, *args, **kwargs):
        request_type = req.GET.get('type', '')
        shop = req.GET.get('shop', '')
        openid = req.GET.get('openid', '')
        if not request_type:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        url = '{}?code={}&shop={}&openid={}'.format(mygzhurl, request_type, shop,
                                                                                              openid)
        return HttpResponseRedirect(url)

    def post(self, req, *args, **kwargs):
        infocode = req.POST.get('infocode', '')
        email = req.POST.get('email', '')
        valemail = ValidateEmail(email)
        if not valemail:
            return Response({'code': 1, 'Message': '请输入一个正确的邮箱'})
        code = ActivationCode.objects.filter(verify_code=infocode, is_use=False)
        if not code:
            return Response({'code': 1, 'Message': '激活码错误'})
        return Response({'code': 0, 'Message': '邮箱和激活码正确'})


@method_decorator(csrf_exempt, name='dispatch')
class ShopOperatorView(APIView):

    def get(self, req, *args, **kwargs):
        openid = req.GET.get('openid', '')
        # 跨域请求
        callback = req.GET.get('callback', '')
        shop = MallShop.objects.filter(openid=openid).first()
        data = []
        data.append({'value': openid, 'label': '店主'})
        if shop:
            operator = Operator.objects.filter(shop=shop, is_status=True)
            for i in operator:
                data.append({'value': i.users.openid, 'label': i.name})
        if callback:
            # 处理跨域请求
            return HttpResponse("%s('%s')" % (callback, json.dumps({'userinfo': data})),
                                status=status.HTTP_200_OK)
        return Response(data)


class GetKaInfoView(APIView):
    def get(self, req, *args, **kwargs):
        _id = req.GET.get('_id', '')
        if _id:
            userka = Userbanka.objects.get(id=_id)
            new_obj = MallServiceUserGoods.objects.filter(usergoods=userka.usergoods)
            data = []
            for i in new_obj:
                number = 0
                userexpend = UserExpend.objects.filter(user_service=i.mallservice, status=False, name=userka.users)
                if userexpend:
                    for up in userexpend:
                        if i.usergoods == up.ka.usergoods:
                            number += up.number
                mallservice = i.mallservice.name
                count = i.count - number
                icon = i.mallservice.icon
                id_ = i.id
                data.append({
                    'url': icon.url,
                    'name': mallservice,
                    'num': count,
                    'id': id_
                })
            return Response(data)
        return Response({'message': '没有调用'})


class ExpenseInfoView(APIView):
    def get(self, req, *args, **kwargs):
        openid = kwargs.get('openid', '')
        if not openid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            MallUser.objects.get(openid=openid)
        except:
            return Response()
        # UserExpend.objects.filter()
        # return render(req, 'record.html', )
        return Response(status=status.HTTP_400_BAD_REQUEST)
