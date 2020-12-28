# 標準ライブラリ
from django.shortcuts import render, redirect

# 独自ライブラリ
from kakeibo.models import 収入支出明細
from kakeibo.forms import DetailForm, InOutRadioForm
import kakeibo.util.kakeibo_util as util
import mysite.util as base_util

# 定数
VIEW_LIST_URL = '/kakeibo/view_list/'
DISPLAY_ROW_NUM = 1000


def view_list(request):
    """
    支出データ一覧画面のメインメソッド。表示内容のデータを作成、編集する。
    :param request: お作法。ブラウザから送信されたリクエストデータが格納されている。
    :return: なし。このメソッドの実行後、Templateにより画面表示される。
    """

    # 支出データ入力欄の初期値設定の初期化。
    detail_initial_dict = {}
    inout_initial_dict = {}

    # セッションデータの初期化。自画面遷移でなければ初期化する。
    if ('HTTP_REFERER' not in request.META) or ('view_list' not in request.META['HTTP_REFERER']):
        request.session.clear()

    # セッションデータの取得
    inout_kubun = request.session['inout_kubun'] if 'inout_kubun' in request.session else '1'
    kotei_hendo_kubun = request.session['kotei_hendo_kubun'] if 'kotei_hendo_kubun' in request.session else '1'

    # POST処理用の変数
    form_name = ''
    request_data = None
    # リクエストメソッドがPOSTの場合の処理。
    if request.method == 'POST':
        # requestデータとボタンを押したフォームの名前を取得。
        request_data = request.POST  # 画面入力されたデータ
        if 'form_name' in request_data:
            form_name = request_data.get('form_name')

    # 分類制御のラジオボタンの内容を取得
    if form_name == 'change_inout':
        inout_check_form_data = InOutRadioForm(request_data)
        inout_check_form_data.is_valid()
        cleaned_data = inout_check_form_data.cleaned_data
        inout_radio = cleaned_data.get('check')

        # ラジオボタンの内容から値を取得
        inout_radio_split = str(inout_radio).split('_')
        inout_kubun = inout_radio_split[0]
        kotei_hendo_kubun = inout_radio_split[1]

    # 分類プルダウン取得用初期値の初期化
    inout_value_dict = {'inout_kubun': inout_kubun, 'kotei_hendo_kubun': kotei_hendo_kubun}

    # 支出明細の取得。支出データ一覧部の表示に利用する。
    inout_details = 収入支出明細.objects.filter(削除フラグ='0', 収入支出分類コード__収入支出区分=inout_kubun,
                                          収入支出分類コード__固定変動区分=kotei_hendo_kubun).order_by('id').reverse()
    inout_detail_operation = util.InoutDetailTableOperation(inout_details)

    # リクエストメソッドがGETの場合。
    # 初期表示の場合か、支出データの追加登録後、編集時にリダイレクトにて表示される場合が対象。
    if request.method == 'GET':
        data = request.GET  # 画面入力されたデータ

        date = data.get('date')
        classify = data.get('classify')
        row_id = data.get('id')

        req_value = get_req_value(date, classify, row_id)
        detail_initial_dict.update(req_value)

        row_value = get_row_value(inout_detail_operation, row_id)
        detail_initial_dict.update(row_value)

    # データ登録操作
    if form_name == 'submit_data':
        # 入力した値の取得。値の整形もしている。
        detail_form_data = DetailForm(request_data, inout_value_dict=inout_value_dict)  # 画面入力されたデータ
        detail_form_data.is_valid()
        cleaned_data = detail_form_data.cleaned_data

        # 登録時に使用する項目
        date = cleaned_data.get('date')
        classify_person = cleaned_data.get('classify_person')
        name = cleaned_data.get('name')
        money = cleaned_data.get('money')
        is_tax = cleaned_data.get('is_tax')
        row_id = cleaned_data.get('row_id')
        # 収入支出分類と対象者に分割する。
        classify_person_split = classify_person.split('_')
        classify = classify_person_split[0]
        person = classify_person_split[1]

        # 編集時に使用する項目
        _id = request_data.get('id')

        # 登録ボタン押下時処理
        if 'add' in request_data:
            inout_detail_operation.add_upd_row(row_id, date, classify, person, name, money, is_tax)
            req_params = {'date': date, 'classify': classify}
            redirect_url = base_util.URL.get_request_url(VIEW_LIST_URL, req_params)
            return redirect(redirect_url)  # "render"でもいいかと思ったが、リダイレクトしないとブラウザ側で再読み込みを行った場合にフォームの再送信が発生する。

    # データ登録操作
    if form_name == 'delete_data':

        # 削除時に使用する項目
        _id = request_data.get('id')

        # 編集ボタン押下時処理
        if 'edit' in request_data:
            req_params = {'id': _id}
            redirect_url = base_util.URL.get_request_url(VIEW_LIST_URL, req_params)
            return redirect(redirect_url)  # "render"でもいいかと思ったが、リダイレクトしないとブラウザ側で再読み込みを行った場合にフォームの再送信が発生する。

        # 削除ボタン押下時処理
        if 'delete' in request_data:
            inout_detail_operation.del_row(_id)

    # 支出データ入力欄の設定を取得。その際に初期値データも送っている。
    detail_form = DetailForm(initial=detail_initial_dict, inout_value_dict=inout_value_dict)

    # 画面表示する行数は固定
    details = inout_detail_operation.get_some_records(DISPLAY_ROW_NUM)

    # 分類プルダウンを制御するラジオボタンのフォームを取得
    inout_initial_dict['check'] = inout_kubun + '_' + kotei_hendo_kubun
    inout_radio_form = InOutRadioForm(initial=inout_initial_dict)

    # セッションデータの登録
    request.session['inout_kubun'] = inout_kubun
    request.session['kotei_hendo_kubun'] = kotei_hendo_kubun

    # Templateに送るデータの作成。
    context = {
        'details': details,
        'detail_form': detail_form,
        'inout_radio_form': inout_radio_form,
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
