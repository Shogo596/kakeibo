from django.db import models


######################################################
# ◆ファイル説明
# djangoにおけるDBの設定を管理する。
#
# ◆注意点
# ・Modelの変更がDBに反映（migrate）できない場合は、
# 　直接DBの定義を変更してModelと一致させ、"--fake"オプションにてmigrateする。
######################################################


class 収入支出分類マスタ(models.Model):
    """
    支出の分類を管理。支出の分類名と固定費か変動費かを管理。
    """
    収入支出分類コード = models.CharField(primary_key=True, max_length=10, blank=True)
    収入支出分類名 = models.CharField(max_length=100, blank=True, null=True)
    収入支出区分 = models.CharField(max_length=1, blank=True, null=True)
    固定変動区分 = models.CharField(max_length=1, blank=True, null=True)
    対象者区別有無 = models.CharField(max_length=1, blank=True, null=True)
    表示順序 = models.IntegerField(blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)
    objects = models.Manager()  # PyCharmの警告対策に必ず記載しておく。

    def __str__(self):
        return str(self.収入支出分類コード)

    @staticmethod
    def get_row(classify_code):
        return 収入支出分類マスタ.objects.get(収入支出分類コード=classify_code)


class 対象者マスタ(models.Model):
    """
    収支データの対象者を管理。通常は"全員"だが個人に紐づくデータの場合のみ使用する。
    """
    対象者コード = models.CharField(primary_key=True, max_length=10, blank=True)
    対象者名 = models.CharField(max_length=100, blank=True, null=True)
    表示順序 = models.IntegerField(blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)
    objects = models.Manager()  # PyCharmの警告対策に必ず記載しておく。

    def __str__(self):
        return str(self.対象者コード)

    @staticmethod
    def get_row(person_code):
        return 対象者マスタ.objects.get(対象者コード=person_code)

    @staticmethod
    def get_all_member_code():
        return '0000000000'


class 定例支出マスタ(models.Model):
    """
    定例（年１とか月１）の支出を管理。
    """
    収入支出分類コード = models.ForeignKey(収入支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.ForeignKey(対象者マスタ, on_delete=models.PROTECT, default='0000000000', blank=True, null=True)
    開始年月 = models.CharField(default='000000', max_length=6, blank=True, null=True)
    終了年月 = models.CharField(default='999999', max_length=6, blank=True, null=True)
    有効月 = models.CharField(max_length=12, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    備考 = models.CharField(max_length=100, blank=True, null=True)
    作成年月日 = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)
    objects = models.Manager()  # PyCharmの警告対策に必ず記載しておく。

    def __str__(self):
        return str(self.id)

    @staticmethod
    def get_row(row_id):
        return 定例支出マスタ.objects.get(id=row_id)


class 支出基本(models.Model):
    """
    ※現在未使用※
    月ごとのデータを管理。
    """
    # 支出基本id = models.IntegerField(primary_key=True)
    # 収入支出分類コード = models.CharField(unique=True, max_length=10, blank=True, null=True)
    支出分類コード = models.ForeignKey(収入支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.CharField(unique=True, max_length=10, blank=True, null=True)
    開始年月 = models.CharField(default='000000', unique=True, max_length=6, blank=True, null=True)
    終了年月 = models.CharField(default='999999', max_length=6, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    作成年月日 = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)
    objects = models.Manager()  # PyCharmの警告対策に必ず記載しておく。

    def __str__(self):
        return str(self.id)


class 収入支出明細(models.Model):
    """
    日ごとの支出データを管理。
    """
    # 支出明細id = models.IntegerField(primary_key=True)
    対象年月日 = models.CharField(max_length=8, blank=True, null=True)
    収入支出分類コード = models.ForeignKey(収入支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.ForeignKey(対象者マスタ, on_delete=models.PROTECT, default='0000000000', blank=True, null=True)
    項目名 = models.CharField(max_length=100, blank=True, null=True)
    金額 = models.IntegerField(blank=True, null=True)
    作成年月日 = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)
    objects = models.Manager()  # PyCharmの警告対策に必ず記載しておく。

    def __str__(self):
        return str(self.id)

    @staticmethod
    def get_row(row_id):
        return 収入支出明細.objects.get(id=row_id)


class カード支出明細(models.Model):
    """
    カードの支出を管理
    """
    支払月 = models.CharField(max_length=6, blank=True, null=True)
    支払方法 = models.CharField(max_length=10, blank=True, null=True)
    利用日 = models.CharField(max_length=8, blank=True, null=True)
    利用店名 = models.CharField(max_length=100, blank=True, null=True)
    利用者 = models.CharField(max_length=10, blank=True, null=True)
    利用金額 = models.IntegerField(blank=True, null=True)
    収入支出分類コード = models.ForeignKey(収入支出分類マスタ, on_delete=models.PROTECT, blank=True, null=True)
    対象者コード = models.ForeignKey(対象者マスタ, on_delete=models.PROTECT, blank=True, null=True)
    備考 = models.CharField(max_length=100, blank=True, null=True)
    作成年月日 = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    更新年月日 = models.DateTimeField(auto_now=True, blank=True, null=True)
    削除フラグ = models.CharField(default='0', max_length=1, blank=True, null=True)
    objects = models.Manager()  # PyCharmの警告対策に必ず記載しておく。

    def __str__(self):
        return str(self.id)

    @staticmethod
    def get_row(row_id):
        return カード支出明細.objects.get(id=row_id)
