from random import randint

from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render
import logging

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE


logger = logging.getLogger('django')


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供注册界面
        :param request: 请求对象
        :return: 注册界面
        """

        return render(request, 'register.html')


class ImageCodeView(View):

    def get(self, request):
        # 获取前端传递过来的参数
        uuid = request.GET.get('uuid')
        # 判断参数是否为None
        if uuid is None:
            return HttpResponseBadRequest('请求参数错误')
        # 获取验证码内容和验证码图片二进制数据
        text, image = captcha.generate_captcha()
        # 将图片内容保存到redis中，并设置过期时间
        redis_conn = get_redis_connection('default')
        redis_conn.setex(f'img:{uuid}', 300, text)
        # 返回响应，将生成的图片以content_type为image/jpeg的形式返回给请求
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):

    def get(self, request):
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        mobile = request.GET.get('mobile')

        # 校验参数
        if not all([image_code_client, uuid, mobile]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 创建连接到redis的对象
        redis_conn = get_redis_connection('default')
        # 提取图形验证码
        image_code_server = redis_conn.get(f'img:{uuid}')
        if image_code_server is None:
            # 图形验证码过期或不存在
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete(f'img:{uuid}')
        except Exception as e:
            logger.error(e)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code_client.lower() != image_code_server.lower():  # 比较小宝
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码: 生成6位数验证码
        sms_code = '%06d' % randint(0, 999999)
        # 将验证码输出在控制台, 以方便调试
        logger.info(sms_code)
        # 保存短信验证码到redis中，并设置有效期
        redis_conn.setex(f'sms:{mobile}', 300, sms_code)
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
