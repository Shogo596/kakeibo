from kakeibo.models import 支出明細, 支出分類マスタ, 対象者マスタ
from mysite.util  import calc_date

# 定数
TAX = 1.1


def add_upd_detail_row(date, classify, person, name, money, is_tax, upd_flg):
    """
    支出明細テーブルに支出データを更新する。
    :param date: 対象年月日
    :param classify: 支出分類コード
    :param person: 対象者コード
    :param name: 項目名
    :param money: 金額
    :param is_tax: 税込計算するかどうか
    :return: なし。
    """
    # 税込計算。入力された金額に税額を加える。
    if is_tax is True:
        money = money * TAX

    if upd_flg == '1':
        # defaults以外をキーとして、データがあればINSERT、データがなければdefaultで値を更新する。
        支出明細.objects.update_or_create(
            対象年月日=date,
            支出分類コード=支出分類マスタ.objects.get(支出分類コード=classify),
            対象者コード=対象者マスタ.objects.get(対象者コード=person),
            項目名=name,
            削除フラグ='0',
            defaults={
                '金額': money,
            },
        )
    else:
        支出明細.objects.create(
            対象年月日=date,
            支出分類コード=支出分類マスタ.objects.get(支出分類コード=classify),
            対象者コード=対象者マスタ.objects.get(対象者コード=person),
            項目名=name,
            削除フラグ='0',
            金額=money,
        )


def delete_table_rows(table_records):
    """
    任意のテーブルからレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
    :param table_records: 任意のテーブル（QuerySet）。削除対象データのみ。
    :return: なし。
    """
    # 削除フラグを更新する。
    table_records.update(削除フラグ='1')


def delete_detail_row(row_id):
    """
    支出明細テーブルから支出データレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
    :param row_id: 削除する行番号。
    :return: なし。
    """
    # 物理削除はやめた。
    # detail_id = data['id']
    # 支出明細.objects.filter(id=detail_id).delete()

    # 削除フラグを更新する。
    支出明細.objects.filter(id=row_id).update(削除フラグ='1')
