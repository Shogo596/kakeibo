import os
import mysite.util as base_util
import kakeibo

# 定数
_SQL_DIR_PATH = os.path.dirname(os.path.abspath(kakeibo.__file__)) + '\\sql'  # SQLファイルが格納されているフォルダまでのパス
_ENCODING = 'utf-8'  # SQLファイルのエンコード


class Operation:
    @staticmethod
    def execute(file_name, params: list) -> list:
        """
        SQL実行
        :param file_name: 実行するSQLファイルの名前
        :param params: SQL実行時のパラメータ
        :return: SQLの実行結果。dict型で返す。
        """
        # SQLファイルの内容取得
        file_path = _SQL_DIR_PATH + '\\' + file_name
        # SQLファイル読み込み。
        sql = base_util.File.get_file_context(file_path, _ENCODING)

        return base_util.DB.sql_exec_some_statement(sql, params)


class SqlFileClassBase:
    _file_name = ''
    _params = []

    @staticmethod
    def get_sql_params(**kwargs):
        pass

    def execute(self):
        return Operation.execute(self._file_name, self._params)


class MonthlyInoutMoney(SqlFileClassBase):
    _FILE_NAME = 'monthly_inout_money.sql'

    def __init__(self, start_ym, end_ym, in_out_kubun, kotei_hendo_kubun):
        self._file_name = self._FILE_NAME
        self._params = [
            start_ym,
            end_ym,
            in_out_kubun,
            kotei_hendo_kubun,
        ]

    @staticmethod
    def get_sql_params(yyyymm, period, in_out_kubun, kotei_hendo_kubun):
        """
        ！！今は使っていない！！
        「monthly_inout_money.sql」の実行時パラメータを取得。
        :param yyyymm: 表示年月
        :param period: 表示期間
        :param in_out_kubun: 収入支出区分
        :param kotei_hendo_kubun: 固定変動区分
        :return: パラメータのList
        """
        start_ym = yyyymm
        end_ym = base_util.Date.calc_date(start_ym, 0, period - 1, 0)
        params = [
            start_ym,
            end_ym,
            in_out_kubun,
            kotei_hendo_kubun,
        ]
        return params


class PeriodInoutMoney(SqlFileClassBase):
    _FILE_NAME = 'period_inout_money.sql'
    start_ym = ''
    end_ym = ''
    in_out_kubun = ''
    kotei_hendo_kubun = ''

    def __init__(self):
        self._file_name = self._FILE_NAME

    def set_params(self, start_ym, end_ym, in_out_kubun, kotei_hendo_kubun):
        self.start_ym = start_ym
        self.end_ym = end_ym
        self.in_out_kubun = in_out_kubun
        self.kotei_hendo_kubun = kotei_hendo_kubun

    def execute(self):
        self._params = [
            self.start_ym,
            self.end_ym,
            self.in_out_kubun,
            self.kotei_hendo_kubun,
        ]

        return Operation.execute(self._file_name, self._params)


class PeriodClassifyInoutMoney(SqlFileClassBase):
    _FILE_NAME = 'period_classify_inout_money.sql'
    start_ym = ''
    end_ym = ''
    in_out_kubun = ''
    kotei_hendo_kubun = ''

    def __init__(self):
        self._file_name = self._FILE_NAME

    def set_params(self, start_ym, end_ym, in_out_kubun, kotei_hendo_kubun):
        self.start_ym = start_ym
        self.end_ym = end_ym
        self.in_out_kubun = in_out_kubun
        self.kotei_hendo_kubun = kotei_hendo_kubun

    def execute(self):
        self._params = [
            self.start_ym,
            self.end_ym,
            self.in_out_kubun,
            self.kotei_hendo_kubun,
        ]

        return Operation.execute(self._file_name, self._params)
