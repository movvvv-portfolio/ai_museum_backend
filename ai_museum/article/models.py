from django.db import models

from django.utils import timezone
from datetime import timezone

# Create your models here.

class Article(models.Model):
    user = models.ForeignKey('user.User', verbose_name="작성자", on_delete=models.CASCADE)
    result_img = models.ImageField()
    content = models.TextField(verbose_name="게시글 작성")
    likes = models.ManyToManyField('user.User', related_name='article_like')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    exposure_start = models.DateField('노출 시작 일자', default=timezone.now)
    exposure_end = models.DateField('노출 종료 일자', default=timezone.now)

class Comment(models.Model):
    user = models.ForeignKey('user.User', verbose_name="작성자", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name="좋아요 게시글")
    comment = models.TextField(verbose_name="댓글")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)