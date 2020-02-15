from kakeibo.models import 支出明細, 支出分類マスタ, 対象者マスタ, カード支出明細
# import mysite.util as util
from django.db.models.query import QuerySet
import kakeibo.util.credit_card as cc

# 定数
TAX = 1.1

# マスタデータ
classify_master = 支出分類マスタ.objects.filter(削除フラグ='0').order_by('表示順序')
person_master = 対象者マスタ.objects.filter(削除フラグ='0').order_by('表示順序')


def add_upd_detail_row(date, classify, person, name, money, is_tax, upd_flg):
    """
    支出明細テーブルに支出データを更新する。
    :param date: 対象年月日
    :param classify: 支出分類コード
    :param person: 対象者コード
    :param name: 項目名
    :param money: 金額
    :param is_tax: 税込計算するかどうか
    :param upd_flg: '0'→insert、'1'→update
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
    :memo 上の関数と統合させたい。
    支出明細テーブルから支出データレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
    :param row_id: 削除する行番号。
    :return: なし。
    """
    # 物理削除はやめた。
    # detail_id = data['id']
    # 支出明細.objects.filter(id=detail_id).delete()

    # 削除フラグを更新する。
    支出明細.objects.filter(id=row_id).update(削除フラグ='1')


def get_classify_person_combobox(kotei_hendo_kubun):
    result = [('', '')]  # comboboxの先頭は空白に。

    classify_person_list = get_classify_person_list(kotei_hendo_kubun)
    for classify_person_row in classify_person_list:
        classify_person_row: ClassifyPersonData = classify_person_row
        result.append((classify_person_row.classify + '_' + classify_person_row.person,
                       classify_person_row.get_classify_person_name()))

    return result


def get_classify_person_list(kotei_hendo_kubun):
    result = []

    classify_records = classify_master
    person_records = person_master

    if kotei_hendo_kubun != '':
        classify_records = classify_master.filter(固定変動区分=kotei_hendo_kubun)

    for classify_row in classify_records:

        person_records = person_records.exclude(対象者コード=対象者マスタ.get_all_member_code())
        for person_row in person_records:

            if classify_row.対象者区別有無 == '1':
                classify_person_data = ClassifyPersonData(classify_row.支出分類コード, person_row.対象者コード)
            else:
                classify_person_data = ClassifyPersonData(classify_row.支出分類コード, 対象者マスタ.get_all_member_code())

            result.append(classify_person_data)

            if classify_row.対象者区別有無 != '1':
                break

    return result


class ClassifyPersonData:
    classify = ''
    person = ''

    def __init__(self, classify, person):
        self.classify = classify
        self.person = person

    def get_classify_person_name(self):
        classify_row = classify_master.filter(支出分類コード=self.classify)[0]
        person_row = person_master.filter(対象者コード=self.person)[0]

        result = classify_row.支出分類名

        if self.person != '0000000000':
            result += '(' + person_row.対象者名 + ')'

        return result


class TableOperationBase:
    def __init__(self, master: QuerySet):
        self._records = master

    def get_row(self, row_id):
        return self._records.filter(id=row_id).first()

    def get_all_records(self):
        return self._records.all()


class CardDetailTableContainer:
    def __init__(self, table_list=None):
        self.table_list = table_list if table_list is not None else []

    def set_row(self, row):
        self.table_list.append(row)

    def get_list(self):
        return self.table_list


class CardDetailTableOperation(TableOperationBase):
    def __init__(self, card_detail_master: QuerySet):
        super().__init__(card_detail_master)
        self.__card_detail_records = self._records

    def get_records_using_dict(self, condition: dict):
        return self.__card_detail_records.filter(**condition)

    def get_month_records(self, yyyymm):
        return self.__card_detail_records.filter(支払月=yyyymm)

    def ins_row(self, yyyymm, card_data_list: cc.CreditCardDataList):
        del_records = self.get_month_records(yyyymm)
        del_records.update(削除フラグ='1')

        for card_data in card_data_list.get_data_list():
            card_data: cc.CreditCardData = card_data

            ins_upd_data = {}
            if card_data.classify_code != '':
                ins_upd_data['支出分類コード'] = \
                    支出分類マスタ.objects.get(支出分類コード=card_data.classify_code)
            if card_data.classify_code != '':
                ins_upd_data['対象者コード'] = 対象者マスタ.objects.get(対象者コード=card_data.person_code)
            ins_upd_data['備考'] = card_data.remarks

            # defaults以外をキーとして、データがあればINSERT、データがなければdefaultで値を更新する。
            self.__card_detail_records.update_or_create(
                支払月=yyyymm,
                支払方法=card_data.payment_method,
                利用日=card_data.use_date,
                利用店名=card_data.shop_name,
                利用者=card_data.person,
                利用金額=card_data.use_money,
                defaults=ins_upd_data,
            )

    def upd_row(self, card_data_list: cc.CreditCardDataList):
        update_records = []
        update_fields = ['支出分類コード', '対象者コード', '備考']

        for card_data in card_data_list.get_data_list():
            card_data: cc.CreditCardData = card_data

            if card_data.is_table_record():
                row: カード支出明細 = self.get_row(card_data.table_id)
                if card_data.classify_code != '':
                    row.支出分類コード = 支出分類マスタ.get_row(card_data.classify_code)
                if card_data.classify_code != '':
                    row.対象者コード = 対象者マスタ.get_row(card_data.person_code)
                row.備考 = card_data.remarks
                update_records.append(row)

        self.__card_detail_records.bulk_update(update_records, fields=update_fields)

    def del_row(self, card_data_list: cc.CreditCardDataList):
        update_records = []
        update_fields = ['削除フラグ']

        for card_data in card_data_list.get_data_list():
            card_data: cc.CreditCardData = card_data

            if card_data.is_table_record():
                row: カード支出明細 = self.get_row(card_data.table_id)
                row.削除フラグ = '1'
                update_records.append(row)

        self.__card_detail_records.bulk_update(update_records, fields=update_fields)
