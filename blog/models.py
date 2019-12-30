from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class ShisyutuKihon(models.Model):
    支出基本id = models.IntegerField(db_column='支出基本ID', primary_key=True)  # Field name made lowercase.
    支出分類コード = models.CharField(unique=True, max_length=10, blank=True, null=True)
    対象者コード = models.CharField(unique=True, max_length=10, blank=True, null=True)
    開始年月 = models.CharField(unique=True, max_length=6, blank=True, null=True)
    終了年月 = models.CharField(max_length=6, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    作成年月日 = models.DateTimeField(blank=True, null=True)
    更新年月日 = models.DateTimeField(blank=True, null=True)
    削除フラグ = models.CharField(max_length=1, blank=True, null=True)

    def publish(self):
        self.save()

    def __str__(self):
        return self.支出分類コード

    class Meta:
        managed = False
        db_table = '支出基本'
