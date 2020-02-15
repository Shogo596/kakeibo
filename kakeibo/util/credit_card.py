class CreditCardDataList:
    def __init__(self):
        self._data_list = []  # CardDataを格納

    def set_row(self, card_data):
        card_data: CreditCardData = card_data
        self._data_list.append(card_data)

    def set_csv_data(self, csv_file):
        pass

    def set_card_detail_table_data(self, card_detail_records):
        for card_detail_row in card_detail_records:
            card_data = CreditCardData()
            card_data.table_id = card_detail_row.id
            card_data.use_date = card_detail_row.利用日
            card_data.shop_name = card_detail_row.利用店名
            card_data.person = card_detail_row.利用者
            card_data.payment_method = card_detail_row.支払方法
            card_data.use_money = card_detail_row.利用金額
            card_data.classify_code = card_detail_row.支出分類コード
            card_data.person_code = card_detail_row.対象者コード
            card_data.remarks = card_detail_row.備考

            self._data_list.append(card_data)

    def get_data_list(self):
        return self._data_list

    def get_total_use_money(self) -> int:
        """
        CardDataの利用金額の合計を取得
        :return:合計値
        """
        result = 0
        for data in self._data_list:
            data: CreditCardData = data
            result += data.use_money
        return result


class RakutenCardDataList(CreditCardDataList):
    def set_csv_data(self, csv_file):
        for line in csv_file:
            card_data = RakutenCardData()
            card_data.use_date = str(line['利用日']).replace('/', '')
            card_data.shop_name = str(line['利用店名・商品名'])
            card_data.person = str(line['利用者'])
            card_data.payment_method = str(line['支払方法'])
            card_data.use_money = int(line['利用金額'])
            card_data.commission = int(line['支払手数料'])
            card_data.all_money = int(line['支払総額'])
            self.set_row(card_data)


class CreditCardData:
    table_id = 0
    use_date = ''
    shop_name = ''
    person = ''
    payment_method = ''
    use_money = 0
    classify_code = ''
    person_code = ''
    remarks = ''

    def is_table_record(self):
        return True if self.table_id != 0 else False


class RakutenCardData(CreditCardData):
    commission = 0
    all_money = 0
