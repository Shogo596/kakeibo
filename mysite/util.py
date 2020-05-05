from dateutil import relativedelta
from datetime import datetime
from django.db import connection
from collections import namedtuple
from urllib.parse import urlencode


# 以下、それぞれクラス化したい。
############################################################################################
# 日付操作
############################################################################################
class Date:
    @staticmethod
    def calc_date(date, addyear, addmonth, addday):
        """
        日付計算
        :param date: 日付（文字列。4桁 or 6桁 or 8桁のみ。）
        :param addyear: 計算値（マイナス値可能）
        :param addmonth: 計算値（マイナス値可能）
        :param addday: 計算値（マイナス値可能）
        :return: 日付計算結果
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

    @staticmethod
    def add_slash(date: str):
        """
        日付文字列にスラッシュを追加する。
        :param date: 日付（文字列。4桁 or 6桁 or 8桁のみ。）
        :return: スラッシュを追加した文字列
        """
        # 引数「日付」の文字長を取得
        date_len = len(date)

        # 日付に応じてスラッシュを追加する。
        result = ''
        if date_len == 4:
            result = date
        if date_len == 6:
            result = STR.insert_str(date, '/', 4)
        if date_len == 8:
            wk = STR.insert_str(date, '/', 6)
            result = STR.insert_str(wk, '/', 4)

        return result


############################################################################################
# ファイル操作
############################################################################################
class File:
    @staticmethod
    def get_file_context(file_path, encoding):
        """
        受け取ったファイルパスのファイル内容を返す。
        :param file_path: ファイルパス
        :param encoding: エンコード
        :return: ファイル内容
        """
        with open(file_path, encoding=encoding) as file:
            file_context = file.read()
        return file_context


############################################################################################
# DB操作
############################################################################################
class DB:
    @staticmethod
    def sql_exec(sql: str, params: list) -> list:
        """
        SQL実行
        :param sql: 実行するSQLファイルの内容
        :param params: SQL実行時のパラメータ
        :return: SQLの実行結果。dict型のリストで返す。
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = DB._dict_fetch(cursor)
        return result

    @staticmethod
    def sql_exec_some_statement(sql: str, params: list) -> list:
        """
        SQL実行（1度に複数ステートメント実行する場合）
        :param sql: 実行するSQLファイルの内容
        :param params: SQL実行時のパラメータ
        :return: SQLの実行結果。dict型のリストで返す。
        """
        param_count = 0
        with connection.cursor() as cursor:
            # 1度の実行で複数ステートメント実行ができないので';'で分割して実行する。
            for sql_part in str(sql).split(';'):
                if sql_part.strip() != "":
                    # '%s'がsqlステートメントに含まれている場合はパラメータ込みで実行する。
                    if '%s' in sql_part:
                        cursor.execute(sql_part, [params[param_count]])
                        param_count = param_count + 1
                    else:
                        cursor.execute(sql_part)

            # SQLの実行結果をdict型に変換する。namedtuple型で返したい場合は「namedtuple_fetch」を使う。
            result = DB._dict_fetch(cursor)
            # result = DB._namedtuple_fetch(cursor)

        return result

    @staticmethod
    def _namedtuple_fetch(cursor):
        """
        SQLの実行結果（cursor）を受け取り、その内容をnamedtuple型（"."でアクセスできる）で返す。
        :param cursor: SQLの実行結果のカーソル
        :return: 実行結果をnamedtuple型のリストで返す。
        """
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]

    @staticmethod
    def _dict_fetch(cursor):
        """
        SQLの実行結果（cursor）を受け取り、その内容をdict型で返す。
        :param cursor: SQLの実行結果のカーソル
        :return: 実行結果をnamedtuple型のリストで返す。
        """
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


############################################################################################
# 文字列操作
############################################################################################
class STR:
    @staticmethod
    def insert_str(base_str, ins_str, point: int):
        """
        文字列に文字列を挿入する。
        :param base_str: 挿入元の文字列
        :param ins_str: 挿入先の文字列
        :param point: 挿入場所（何文字目か）
        :return: 挿入した文字列
        """
        return '{0}{1}{2}'.format(base_str[:point], ins_str, base_str[point:])


############################################################################################
# FormSet操作
############################################################################################
class FormSet:
    @staticmethod
    def set_disabled(formset, item_name):
        """
        formsetの指定項目に対してdisabledのフラグが立っていたら、その項目をdisabledにする。
        :param formset: 対象のformset
        :param item_name: disabledとする対象の項目名
        :return: disabled設定後のformset
        """
        item_disabled_name = item_name + '_disabled'
        for i in range(len(formset.forms)):
            if formset.initial[i][item_disabled_name] == '1':
                formset.forms[i].fields[item_name].widget.attrs['disabled'] = 'disabled'
        return formset


############################################################################################
# URL操作
############################################################################################
class URL:
    @staticmethod
    def get_request_url(url, params_dict: dict):
        """
        引数をもとにURLを作成する。引数に値が存在する場合はGETリクエストとしてパラメータを設定する。
        :param url: 遷移先のURL
        :param params_dict: GETリクエストに設定するパラメータ
        :return: GETリクエストのURL
        """
        if params_dict is None or len(params_dict) == 0:
            return url

        # GETリクエストとしてURLを作成する。
        parameters = urlencode(params_dict)
        return f'{url}?{parameters}'
