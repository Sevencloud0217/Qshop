from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from Saller.models import *
import hashlib
from django.core.paginator import Paginator
# Create your views here.

## 登录装饰器
def LoginVaild(func):
    ## 1. 获取cookie中username和email
    ## 2. 判断username和email
    ## 3. 如果成功  跳转
    ## 4. 如果失败   login.html
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get('username')
        ## 获取session
        session_username = request.session.get("username")
        if username and session_username and username == session_username:
            return func(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/Saller/login/')
    return inner

## 密码加密
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

## 注册
def register(request):
    if request.method == "POST":
        error_msg = ""
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email:
            ## 判断邮箱是否存在
            loginuser = LoginUser.objects.filter(email=email).first()
            if not loginuser:
                ## 不存在 写库
                user = LoginUser()
                user.email = email
                user.username = email
                user.password = setPassword(password)
                user.user_type = 0
                user.save()
            else:
                error_msg = "邮箱已经被注册，请登录"
        else:
            error_msg = "邮箱不可以为空"

    return render(request,"saller/register.html",locals())

## 登录
import datetime
import time
def login(request):
    if request.method == "POST":
        error_msg = ""
        email = request.POST.get("email")
        password = request.POST.get("password")
        code = request.POST.get("vaild_code")
        if email:
            user = LoginUser.objects.filter(email=email,user_type=0).first()
            if user:
                ## 存在
                if user.password == setPassword(password):
                    ## 登录成功
                    ## 跳转页面
                    # error_msg = "登录成功"
                    # return HttpResponseRedirect('/index/')
                    ## 设置cookie

                    ## 判断验证码   从库里取验证码
                    vaild_code = Vaild_Code.objects.filter(code_status=0,code_user=email,code_content=code).first()
                    ## 判断时间  有效期2分钟  当前时间 - code创建时间 <= 2min
                    # now = time.time()
                    now = time.mktime(datetime.datetime.now().timetuple())
                    db_time = datetime.datetime.strptime(vaild_code.code_time, "%Y-%m-%d %H:%M:%S")
                    db_time = time.mktime(db_time.timetuple())
                    #
                    if (now - db_time)/ 60 > 2:
                        ## 超时
                        error_msg = "验证码超时"
                    else:
                        response  = HttpResponseRedirect("/Saller/index/")
                        response.set_cookie("username",user.username)
                        response.set_cookie("userid",user.id)
                        request.session['username'] = user.username  ## 设置session
                        vaild_code.code_status = 1
                        vaild_code.save()
                        return response
                else:
                    error_msg = "密码错误"
            else:
                error_msg = "用户不存在"
        else:
            error_msg = "邮箱不可以为空"
    return render(request,"saller/login.html",locals())

## 首页
@LoginVaild
def index(request):
    return render(request,"saller/index.html")

## 登出
def logout(request):
    # 删除cookie   删除  session
    response = HttpResponseRedirect("/Saller/login/")
    # response.delete_cookie("kename")
    keys = request.COOKIES.keys()
    for one in keys:
        response.delete_cookie(one)

    del request.session['username']
    return response
## 商品列表
def goods_list(request,status,page=1):
    """

    :param request:
    :param status: 想要获取的是 在售或者下架的商品   在售传参1   下架是 0
    :param page:   页
    :return:
    """
    page = int(page)
    if status == "0":
        ## 下架商品
        goods_obj = Goods.objects.filter(goods_status = 0).order_by('goods_number')
    else:
        ## 在售商品
        goods_obj = Goods.objects.filter(goods_status = 1).order_by('goods_number')
    goods_all = Paginator(goods_obj,10)
    goods_list = goods_all.page(page)  ##

    return render(request,"saller/goods_list.html",locals())


## 商品状态
def goods_status(request,status,id):
    """
    完成当 下架  修改 status 为 0
    当 上架的   修改status 为 1
    :param request:
    :param status:  操作内容  up 上架    down   下架
     :param id:  商品id
    :return:
    """
    id = int(id)
    goods = Goods.objects.get(id=id)
    if status== "up":
        ###上架
        goods.goods_status = 1
    else:
        ## 下架
        goods.goods_status = 0
    goods.save()
    # return HttpResponseRedirect("/goods_list/1/1/")
    ##  获取请求来源
    url =request.META.get("HTTP_REFERER","/Saller/goods_list/1/1/")
    return HttpResponseRedirect(url)

@LoginVaild
def personal_info(request):
    ##
    user_id = request.COOKIES.get("userid")
    print (user_id)
    user = LoginUser.objects.filter(id = user_id).first()
    if request.method == "POST":
        ## 获取 数据，保存数据
        data = request.POST
        print (data.get("email"))
        user.username = data.get("username")
        user.phone_number = data.get("phone_number")
        user.age = data.get("age")
        user.gender = data.get("gender")
        user.address = data.get("address")
        user.photo = request.FILES.get("photo")
        user.save()
        print (data)
    return render(request,"saller/personal_info.html",locals())

@LoginVaild
def goods_add(request):
    ###  处理post请求，获取数据，保存数据，返回响应
    goods_type = GoodsType.objects.all()
    if request.method == "POST":
        data = request.POST
        print (data)
        goods = Goods()
        goods.goods_number = data.get("goods_number")
        goods.goods_name = data.get("goods_name")
        goods.goods_price = data.get("goods_price")
        goods.goods_count = data.get("goods_count")
        goods.goods_location = data.get("goods_location")
        goods.goods_safe_date = data.get("goods_safe_date")
        goods.picture = request.FILES.get("picture")
        goods.goods_status = 1
        goods.save()
        goods_type = request.POST.get("goods_type")   ## select 标签的value  类型是 string
        # goods.goods_type_id = int(goods_type)
        goods.goods_type = GoodsType.objects.get(id = goods_type)  ## 保存类型
        ## 保存店铺
        ## 从cookie中获取到用户信息
        user_id = request.COOKIES.get("userid")
        goods.goods_store = LoginUser.objects.get(id = user_id)
        goods.save()
    return render(request,"saller/goods_add.html",locals())


import smtplib
from email.mime.text import MIMEText

def send_email(params):
    ## params   字典类型
    """
    :param params:   字典
        subject  主题
        content  邮件内容
        toemail  收件人 列表
    :return:
    """
    subject = params.get("subject")
    content = params.get("content")
    sender = "str_wjp@163.com"
    rec = params.get("toemail")
    password = "qaz123"
    message = MIMEText(content,"plain","utf-8")
    message["Subject"] = subject
    message["From"] = sender   ## 发件人
    message["To"] = str(rec)   ## 收件人
    try:
        smtp = smtplib.SMTP_SSL("smtp.163.com",465)
        smtp.login(sender,password)
        smtp.sendmail(sender,rec,message.as_string())
        smtp.close()
        return True
    except:
        return False

import random
def get_code(request):
    result = {"code":10000,"msg":""}
    ## 获取email
    email = request.GET.get("email")
    print(email)
    ##  判断用户是否存在
    if email:
        ## 判断  email 是否有值
        flag = LoginUser.objects.filter(email = email).exists()
        if flag:
            ## 用户存在
            ##发送验证码
            ##
            code = random.randint(1000,9999)   ## 4位
            content = "您的验证码是%s,打死不要告诉别人"% (code)
            params = dict(subject="登录验证码",content = content,toemail=[email])
            eflag = send_email(params)
            if eflag:
                ## 保存验证码到数据库
                vaile_code = Vaild_Code()
                vaile_code.code_content = code
                vaile_code.code_status = 0
                vaile_code.code_user = email
                now = datetime.datetime.now()
                vaile_code.code_time = now.strftime("%Y-%m-%d %H:%M:%S")
                vaile_code.save()
                result = {"code": 10000, "msg": "验证码发送成功"}
            else:
                result = {"code": 10003, "msg": "未知错误，联系客服"}
        else:
            ## 用户不存在
            result = {"code": 10002, "msg": "用户不存在"}
    else:
        result = {"code": 10001, "msg": "邮箱不能为空"}
    return JsonResponse(result)






