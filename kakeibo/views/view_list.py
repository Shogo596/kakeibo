# 標準ライブラリ
from django.shortcuts import render, redirect

# 独自ライブラリ
from kakeibo.models import 収入支出明細
from kakeibo.forms import DetailForm
import kakeibo.util.kakeibo_util as util
import mysite.util as base_util

# 定数
VIEW_LIST_URL = '/kakeibo/view_list/'
DISPLAY_ROW_NUM = 10


def view_list(request):
    """
    支出データ一覧画面のメインメソッド。表示内容のデータを作成、編集する。
    :param request: お作法。ブラウザから送信されたリクエストデータが格納されている。
    :return: なし。このメソッドの実行後、Templateにより画面表示される。
    """

    # 支出明細の取得。支出データ一覧部の表示に利用する。
    # details = 収入支出明細.objects.order_by('id').reverse()[:20]
    # details = details.reverse()[:20]
    # details = 収入支出明細.objects.filter(削除フラグ='0', 支出分類マスタ__固定変動区分='1').order_by('id').reverse().select_related()
    inout_details = 収入支出明細.objects.filter(削除フラグ='0', 収入支出分類コード__固定変動区分='1').order_by('id').reverse()
    inout_detail_operation = util.InoutDetailTableOperation(inout_details)

    # 支出データ入力欄の初期値設定の初期化。
    initial_value_dict = {}

    # リクエストメソッドがGETの場合。
    # 初期表示の場合か、支出データの追加登録後、編集時にリダイレクトにて表示される場合が対象。
    if request.method == 'GET':
        data = request.GET  # 画面入力されたデータ

        date = data.get('date')
        classify = data.get('classify')
        row_id = data.get('id')

        req_value = get_req_value(date, classify, row_id)
        initial_value_dict.update(req_value)

        row_value = get_row_value(inout_detail_operation, row_id)
        initial_value_dict.update(row_value)

    # リクエストメソッドがPOSTの場合。
    # 登録ボタン押下時もしくは削除ボタン押下時。
    if request.method == 'POST':

        # 入力した値の取得。値の整形もしている。
        request_data = request.POST  # 画面入力されたデータ
        detail_form_data = DetailForm(request_data)  # 画面入力されたデータ
        detail_form_data.is_valid()
        cleaned_data = detail_form_data.cleaned_data

        # 登録時に使用する項目
        date = cleaned_data.get('date')
        classify = cleaned_data.get('classify')
        person = '0000000000'
        name = cleaned_data.get('name')
        money = cleaned_data.get('money')
        is_tax = cleaned_data.get('is_tax')
        row_id = cleaned_data.get('row_id')

        # 削除時に使用する項目
        _id = request_data.get('id')

        # 遷移先のURLの指定
        redirect_url = VIEW_LIST_URL
        req_params = {}

        if 'add' in request_data:
            inout_detail_operation.add_upd_row(row_id, date, classify, person, name, money, is_tax)
            req_params = {'date': date, 'classify': classify}

        elif 'edit' in request_data:
            req_params = {'id': _id}

        elif 'delete' in request_data:
            inout_detail_operation.del_row(_id)

        redirect_url = base_util.URL.get_request_url(redirect_url, req_params)
        return redirect(redirect_url)  # "render"でもいいかと思ったが、リダイレクトしないとブラウザ側で再読み込みを行った場合にフォームの再送信が発生する。

    # 支出データ入力欄の設定を取得。その際に初期値データも送っている。
    form = DetailForm(initial=initial_value_dict)

    # 画面表示する行数は固定
    details = inout_detail_operation.get_some_records(DISPLAY_ROW_NUM)

    # Templateに送るデータの作成。
    context = {
        'details': details,
        'form': form,
    }

    # 支出データ一覧画面の表示。"context"の内容をもとに"view_list.html"が表示される。
    return render(request, 'kakeibo/view_list.html', context)


def get_req_value(date, classify, row_id):
    """
    支出データ入力部の初期値を設定する。
    :param date: 支出データ入力欄の[日付]項目の初期値。
    :param classify: 支出データ入力欄の[分類]項目の初期値。
    :param row_id: 選択したデータの行番号
    :return: 初期値設定を格納するdictionary変数。
    """
    req_value_dict = {}
    if date is not None: req_value_dict['date'] = date
    if classify is not None: req_value_dict['classify'] = classify
    if row_id is not None: req_value_dict['row_id'] = row_id

    return req_value_dict


def get_row_value(inout_detail_operation, row_id):
    """
    引数の行番号のレコードを取得する。
    :param inout_detail_operation: 収入支出詳細テーブル
    :param row_id: 行番号
    :return: 行データのdict
    """
    row = inout_detail_operation.get_row(row_id)
    row_value = {}
    if row is not None:
        row_value['date'] = row.対象年月日
        row_value['classify'] = row.収入支出分類コード
        row_value['name'] = row.項目名
        row_value['money'] = row.金額

    return row_value
