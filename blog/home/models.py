from django.db import models

# Create your models here.
from django.utils import timezone


class ArticleCategory(models.Model):
    """文章分类"""

    title = models.CharField(max_length=100, blank=False)

    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tb_category'
        verbose_name = '类别管理'
        verbose_name_plural = verbose_name
