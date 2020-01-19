from django.db import models
from django.utils import timezone


######################################################
# ◆ファイル説明
# djangoにおけるDBの設定を管理する。
######################################################


class 支出分類マスタ(models.Model):
    """
    支出の分類を管理。支出の分類名と固定費か変動費かを管理。
    """
    支出分類コード = models.CharField(primary_key=True, max_length=10, blank=True)
    支出分類名 = models.CharField(max_length=100, blank=True, null=True)
    固定変動区分 = models.CharField(max_length=1, blank=True, null=True)
    対象者区別有無 = models.CharField(max_length=1, blank=True, null=True)
    表示順序 = models.IntegerField(blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)

    def __str__(self):
        return str(self.支出分類コード)


class 対象者マスタ(models.Model):
    """
    収支データの対象者を管理。通常は"全員"だが個人に紐づくデータの場合のみ使用する。
    """
    対象者コード = models.CharField(primary_key=True, max_length=10, blank=True)
    対象者名 = models.CharField(max_length=100, blank=True, null=True)
    表示順序 = models.IntegerField(blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)

    def __str__(self):
        return str(self.対象者コード)


class 定例支出マスタ(models.Model):
    """
    定例（年１とか月１）の支出を管理。
    """
    支出分類コード = models.ForeignKey(支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.ForeignKey(対象者マスタ, on_delete=models.PROTECT, default='0000000000', blank=True, null=True)
    開始年月 = models.CharField(default='000000', max_length=6, blank=True, null=True)
    終了年月 = models.CharField(default='999999', max_length=6, blank=True, null=True)
    有効月 = models.CharField(max_length=12, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    備考 = models.CharField(max_length=100, blank=True, null=True)
    作成年月日 = models.DateTimeField(default=timezone.now, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class 支出基本(models.Model):
    """
    ※現在未使用※
    月ごとのデータを管理。
    """
    # 支出基本id = models.IntegerField(primary_key=True)
    # 支出分類コード = models.CharField(unique=True, max_length=10, blank=True, null=True)
    支出分類コード = models.ForeignKey(支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.CharField(unique=True, max_length=10, blank=True, null=True)
    開始年月 = models.CharField(default='000000', unique=True, max_length=6, blank=True, null=True)
    終了年月 = models.CharField(default='999999', max_length=6, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    作成年月日 = models.DateTimeField(default=timezone.now, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)

    def __str__(self):
        return str(self.支出基本id)


class 支出明細(models.Model):
    """
    日ごとの支出データを管理。
    """
    # 支出明細id = models.IntegerField(primary_key=True)
    対象年月日 = models.CharField(max_length=8, blank=True, null=True)
    支出分類コード = models.ForeignKey(支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.ForeignKey(対象者マスタ, on_delete=models.PROTECT, default='0000000000', blank=True, null=True)
    項目名 = models.CharField(max_length=100, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    作成年月日 = models.DateTimeField(default=timezone.now, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)

    def __str__(self):
        return str(self.id)


