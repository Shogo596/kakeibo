from dateutil import relativedelta
from datetime import datetime


def calc_date(date, addyear, addmonth, addday):
    """
    日付計算
    :param date: 日付（文字列。4桁 or 6桁 or 8桁のみ。）
    :param addyear: 計算値（マイナス値可能）
    :param addmonth: 計算値（マイナス値可能）
    :param addday: 計算値（マイナス値可能）
    :return:
    """

    # 引数「日付」の文字長を取得
    date_len = len(date)

    # 引数「日付」を調整
    if date_len == 4:
        date += '0401'
    if date_len == 6:
        date += '01'

    # 日付計算
    dt_date = datetime.strptime(date, '%Y%m%d')
    dt_date = dt_date + relativedelta.relativedelta(years=addyear, months=addmonth, days=addday)

    # 戻り値文字列の調整
    result = ''
    if date_len == 4:
        result = dt_date.strftime('%Y')
    if date_len == 6:
        result = dt_date.strftime('%Y%m')
    if date_len == 8:
        result = dt_date.strftime('%Y%m%d')

    return result
