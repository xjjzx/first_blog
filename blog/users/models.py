from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):

    # 电话号码字段
    # unique 为唯一字段
    mobile = models.CharField(max_length=20, unique=True, blank=True)

    # 头像
    # upload_to为保存到响应的子目录中
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)

    # 个人简介
    user_desc = models.TextField(max_length=500, blank=True)

    # 修改认证的字段
    USERNAME_FIELD = 'mobile'

    # 创建超级管理员的账号必须输入的字段
    REQUIRED_FIELDS = ['username', 'email']

    # 内部类class Meta 用于给model定义元数据
    class Meta:
        db_table = 'blog_user'      # 修改默认的表名
        verbose_name = '用户信息'   # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.mobile
