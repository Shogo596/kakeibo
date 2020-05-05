from kakeibo.models import 収入支出明細, 収入支出分類マスタ, 対象者マスタ, カード支出明細, 定例支出マスタ
# import mysite.util as util
from django.db.models.query import QuerySet
import kakeibo.util.credit_card as cc

# 定数
TAX = 1.1

# マスタデータ
classify_master = 収入支出分類マスタ.objects.filter(削除フラグ='0').order_by('表示順序')
person_master = 対象者マスタ.objects.filter(削除フラグ='0').order_by('表示順序')


# def delete_table_rows(table_records):
#     """
#     任意のテーブルからレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
#     :param table_records: 任意のテーブル（QuerySet）。削除対象データのみ。
#     :return: なし。
#     """
#     # 削除フラグを更新する。
#     table_records.update(削除フラグ='1')


def get_classify_person_combobox(kotei_hendo_kubun):
    """
    コンボボックス表示用に「収入支出分類コード_対象者コード」のリストを作成する。
    :param kotei_hendo_kubun: リストに含める固定変動区分を指定する。空の場合はすべての区分となる。
    :return: コンボボックス用のリスト
    """
    result = [('', '')]  # comboboxの先頭は空白に。

    classify_person_list = get_classify_person_list(kotei_hendo_kubun)
    for classify_person_row in classify_person_list:
        classify_person_row: ClassifyPersonData = classify_person_row
        result.append((classify_person_row.classify + '_' + classify_person_row.person,
                       classify_person_row.get_classify_person_name()))

    return result


def get_classify_person_list(kotei_hendo_kubun):
    """
    収入支出分類と対象者のペアをリストで返す。
    :param kotei_hendo_kubun: リストに含める固定変動区分を指定する。空の場合はすべての区分となる。
    :return: ペアのリスト
    """
    result = []

    classify_records = classify_master
    person_records = person_master

    # 固定変動区分で絞り込み
    if kotei_hendo_kubun != '':
        classify_records = classify_master.filter(固定変動区分=kotei_hendo_kubun)

    # 変動費から表示するように逆順にする。
    classify_records = classify_records.order_by('固定変動区分').reverse()

    for classify_row in classify_records:
        # 世帯全員以外の対象者を取得する。
        person_records = person_records.exclude(対象者コード=対象者マスタ.get_all_member_code())
        for person_row in person_records:

            if classify_row.対象者区別有無 == '1':
                classify_person_data = ClassifyPersonData(classify_row.収入支出分類コード, person_row.対象者コード)
            else:
                classify_person_data = ClassifyPersonData(classify_row.収入支出分類コード, 対象者マスタ.get_all_member_code())

            result.append(classify_person_data)

            # 区別しない場合は対象者でループする必要がないからbreak
            if classify_row.対象者区別有無 != '1':
                break

    return result


class ClassifyPersonData:
    """
    収入支出分類と対象者をペアで格納するクラス
    """
    classify = ''
    person = ''

    def __init__(self, classify, person):
        self.classify = classify
        self.person = person

    def get_classify_person_name(self):
        """
        収入支出分類と対象者のペアの名前を返す。
        :return: ペア
        """
        classify_row = classify_master.filter(収入支出分類コード=self.classify)[0]
        person_row = person_master.filter(対象者コード=self.person)[0]

        result = classify_row.収入支出分類名

        # 対象者が世帯全員以外の場合は「収入支出分類（対象者）」にする。
        if self.person != '0000000000':
            result += '(' + person_row.対象者名 + ')'

        return result


class TableOperationBase:
    """
    テーブル操作の基底クラス
    """
    def __init__(self, master: QuerySet):
        self._records = master

    def sort(self, sort_key):
        self._records = self._records.order_by(sort_key)
        return self

    def get_row(self, row_id):
        return self._records.filter(id=row_id).first()

    def get_all_records(self):
        return self._records.all()

    def get_some_records(self, num):
        return self._records.all()[:num]

    def get_records_using_dict(self, condition: dict):
        """
        dictで取得した条件でレコードを返す。
        :param condition: 検索条件
        :return: 取得結果
        """
        return self._records.filter(**condition).all()

    def del_row(self, row_id):
        """
        引数で指定したidのデータレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
        :param row_id: 削除する行番号。
        :return: なし。
        """
        # 削除フラグを更新する。
        self._records.filter(id=row_id).update(削除フラグ='1')

    def del_all(self):
        """
        定義済みのデータレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
        :return: なし。
        """
        # 削除フラグを更新する。
        self._records.update(削除フラグ='1')


class InoutDetailTableOperation(TableOperationBase):
    """
    収入支出明細テーブルの操作クラス
    """
    def __init__(self, inout_detail_master: QuerySet):
        super().__init__(inout_detail_master)
        self.__inout_detail_records = self._records

    def get_row_filter(self, filter_dict: dict):
        """
        任意の項目をキーとしてフィルタしたレコード取得する。
        :param filter_dict: フィルタする項目のdict
        :return: フィルタ結果のレコード
        """
        temp_records: QuerySet = self.__inout_detail_records
        for key, value in filter_dict.items():
            if key == '収入支出分類コード': temp_records = temp_records.filter(収入支出分類コード=value)
            if key == '対象者コード': temp_records = temp_records.filter(対象者コード=value)
        return temp_records.first()

    # def add_upd_row_(self, date, classify, person, name, money, is_tax, upd_flg):
    #     """
    #     支出明細テーブルに支出データを更新する。
    #     :param date: 対象年月日
    #     :param classify: 収入支出分類コード
    #     :param person: 対象者コード
    #     :param name: 項目名
    #     :param money: 金額
    #     :param is_tax: 税込計算するかどうか
    #     :param upd_flg: '0'→insert、'1'→update
    #     :return: なし。
    #     """
    #
    #     # 税込計算
    #     money = self.calc_tax(money, is_tax)
    #
    #     if upd_flg == '1':
    #         # defaults以外をキーとして、データがあればINSERT、データがなければdefaultで値を更新する。
    #         self.__inout_detail_records.update_or_create(
    #             対象年月日=date,
    #             収入支出分類コード=収入支出分類マスタ.objects.get(収入支出分類コード=classify),
    #             対象者コード=対象者マスタ.objects.get(対象者コード=person),
    #             項目名=name,
    #             削除フラグ='0',
    #             defaults={
    #                 '金額': money,
    #             },
    #         )
    #     else:
    #         self.__inout_detail_records.create(
    #             対象年月日=date,
    #             収入支出分類コード=収入支出分類マスタ.objects.get(収入支出分類コード=classify),
    #             対象者コード=対象者マスタ.objects.get(対象者コード=person),
    #             項目名=name,
    #             削除フラグ='0',
    #             金額=money,
    #         )

    def add_upd_row(self, row_id, date, classify, person, name, money, is_tax):
        """
        支出明細テーブルに支出データを更新する。
        :param row_id: 行番号
        :param date: 対象年月日
        :param classify: 収入支出分類コード
        :param person: 対象者コード
        :param name: 項目名
        :param money: 金額
        :param is_tax: 税込計算するかどうか
        :return: なし。
        """
        # 税込計算
        money = self.calc_tax(money, is_tax)

        self.__inout_detail_records.update_or_create(
            id=row_id,
            defaults={
                '対象年月日': date,
                '収入支出分類コード': 収入支出分類マスタ.objects.get(収入支出分類コード=classify),
                '対象者コード': 対象者マスタ.objects.get(対象者コード=person),
                '項目名': name,
                '金額': money,
            },
        )

    @staticmethod
    def calc_tax(money, is_tax):
        """
        税込計算。入力された金額に税額を加える。
        :param money: 税込計算対象の金額
        :param is_tax: 税込計算有無
        :return: 税込計算後の金額
        """
        if is_tax is True:
            money = money * TAX
        return money


class CardDetailTableOperation(TableOperationBase):
    """
    カード支出明細テーブルの操作クラス
    """
    def __init__(self, card_detail_master: QuerySet):
        super().__init__(card_detail_master)
        self.__card_detail_records = self._records

    def get_month_records(self, yyyymm):
        return self.__card_detail_records.filter(支払月=yyyymm)

    def get_row_filter(self, filter_dict: dict):
        temp_records: QuerySet = self.__card_detail_records
        for key, value in filter_dict.items():
            if key == '収入支出分類コード': temp_records = temp_records.filter(収入支出分類コード=value)
            if key == '対象者コード': temp_records = temp_records.filter(対象者コード=value)
        return temp_records.first()

    def ins_rows(self, yyyymm, card_data_list: cc.CreditCardDataList):
        """
        引数の年月についてdelete-insertする。
        :param yyyymm: insertする支払月の指定
        :param card_data_list: insertデータの中身
        """
        del_records = self.get_month_records(yyyymm)
        del_records.update(削除フラグ='1')

        for card_data in card_data_list.get_data_list():
            card_data: cc.CreditCardData = card_data

            ins_upd_data = {}
            if card_data.classify_code != '':
                ins_upd_data['収入支出分類コード'] = \
                    収入支出分類マスタ.objects.get(収入支出分類コード=card_data.classify_code)
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

    def upd_rows(self, card_data_list: cc.CreditCardDataList):
        """
        収入支出分類コード、対象者コード、備考を更新する。
        :param card_data_list: 更新対象データ
        """
        update_records = []
        update_fields = ['収入支出分類コード', '対象者コード', '備考']

        for card_data in card_data_list.get_data_list():
            card_data: cc.CreditCardData = card_data

            if card_data.is_table_record():
                row: カード支出明細 = self.get_row(card_data.table_id)
                if card_data.classify_code != '':
                    row.収入支出分類コード = 収入支出分類マスタ.get_row(card_data.classify_code)
                if card_data.classify_code != '':
                    row.対象者コード = 対象者マスタ.get_row(card_data.person_code)
                row.備考 = card_data.remarks
                update_records.append(row)

        self.__card_detail_records.bulk_update(update_records, fields=update_fields)

    def del_rows(self, card_data_list: cc.CreditCardDataList):
        """
        削除する。
        :param card_data_list: 削除対象データ
        """
        update_records = []
        update_fields = ['削除フラグ']

        for card_data in card_data_list.get_data_list():
            card_data: cc.CreditCardData = card_data

            if card_data.is_table_record():
                row: カード支出明細 = self.get_row(card_data.table_id)
                row.削除フラグ = '1'
                update_records.append(row)

        self.__card_detail_records.bulk_update(update_records, fields=update_fields)
