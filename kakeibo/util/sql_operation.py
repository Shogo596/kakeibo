import os
import mysite.util as base_util

# 定数
_SQL_DIR_PATH = os.getcwd() + '\\..\\kakeibo\\sql'  # SQLファイルが格納されているフォルダまでのパス
_ENCODING = 'utf-8'  # SQLファイルのエンコード


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
