from django.shortcuts import render, redirect
from .models import 支出明細, 支出分類マスタ
from .forms import DetailForm
# from django.utils import timezone
from urllib.parse import urlencode

# 定数
VIEW_LIST_URL = '/kakeibo/'

def view_list(request):
    """
    支出データ一覧画面のメインメソッド。表示内容のデータを作成、編集する。
    :param request: お作法。ブラウザから送信されたリクエストデータが格納されている。
    :return: なし。このメソッドの実行後、Templateにより画面表示される。
    """

    # 支出明細の取得。支出データ一覧部の表示に利用する。
    # details = 支出明細.objects.order_by('id').reverse()[:20]
    # details = details.reverse()[:20]
    details = 支出明細.objects.filter(削除フラグ='0').order_by('id').reverse().select_related()

    # 支出データ入力欄の初期値設定の初期化。
    initial_value_dict = {
        'date': '',
        'classify': '',
    }

    # リクエストメソッドがGETの場合。
    # 初期表示の場合か、支出データの追加登録後にリダイレクトにて表示される場合が対象。
    if request.method == 'GET':
        data = request.GET  # 画面入力されたデータ

        _date = data.get('date')
        _classify = data.get('classify')

        # GETリクエストとして初期値が設定されている場合。（リダイレクトされてきた場合）
        if _date is not None and _classify is not None:
            set_initial_value(_date, _classify, initial_value_dict)

    # リクエストメソッドがPOSTの場合。
    # 登録ボタン押下時もしくは削除ボタン押下時。
    if request.method == 'POST':

        # 入力した値の取得。値の整形もしている。
        request_data = request.POST  # 画面入力されたデータ
        detail_form_data = DetailForm(request_data)  # 画面入力されたデータ
        detail_form_data.is_valid()
        cleaned_data = detail_form_data.cleaned_data

        # 登録時に使用する項目
        _date = cleaned_data.get('date')
        _classify = cleaned_data.get('classify')
        _name = cleaned_data.get('name')
        _money = cleaned_data.get('money')
        _is_tax = cleaned_data.get('tax')

        # 削除時に使用する項目
        _detail_id = request_data.get('id')

        if 'add' in request_data:
            add_row(_date, _classify, _name, _money, _is_tax)

        elif 'delete' in request_data:
            delete_row(_detail_id)

        redirect_url = get_url_view_list(_date, _classify)
        return redirect(redirect_url)  # "render"でもいいかと思ったが、リダイレクトしないとブラウザ側で再読み込みを行った場合にフォームの再送信が発生する。

    # 支出データ入力欄の設定を取得。その際に初期値データも送っている。
    form = DetailForm(initial=initial_value_dict)

    # Templateに送るデータの作成。
    context = {
        'details': details,
        'form': form,
    }

    # 支出データ一覧画面の表示。"context"の内容をもとに"view_list.html"が表示される。
    return render(request, 'kakeibo/view_list.html', context)


def add_row(_date, _classify, _name, _money, _is_tax):
    """
    支出明細テーブルに画面入力された支出データを登録する。
    :param _date: 対象年月日
    :param _classify: 支出分類コード
    :param _name: 項目名
    :param _money: 金額
    :param _is_tax: 税込計算するかどうか
    :return: なし。
    """
    # DB的には日付は数値8桁のため整形。
    _str_date = _date.strftime('%Y%m%d')

    # 税込計算。入力された金額に税額を加える。
    if _is_tax is True:
        _money = _money * 1.1

    支出明細.objects.create(
        対象年月日=_str_date,
        支出分類コード=支出分類マスタ.objects.get(支出分類コード=_classify),
        項目名=_name,
        金額=_money,
    )


def delete_row(_id):
    """
    支出明細テーブルから支出データレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
    :param _id: 削除ボタン押下時の行番号。
    :return: なし。
    """
    # 物理削除はやめた。
    # detail_id = data['id']
    # 支出明細.objects.filter(id=detail_id).delete()

    # 削除フラグを更新する。
    detail_row = 支出明細.objects.filter(id=_id).first()
    detail_row.削除フラグ = '1'
    detail_row.save()


def get_url_view_list(_date, _classify):
    """
    支出データ一覧画面のURLを取得する。引数に値が存在する場合はGETリクエストとしてパラメータを設定する。
    :param _date: 支出データ入力欄の[日付]項目の初期値。初期値を表示する場合のみ設定。
    :param _classify: 支出データ入力欄の[分類]項目の初期値。初期値を表示する場合のみ設定。
    :return: 支出データ一覧画面のURL。
    """
    redirect_url = VIEW_LIST_URL

    if _date is None and _classify is None:
        return redirect_url

    # GETリクエストとしてURLを作成する。
    parameters = urlencode({'date': _date, 'classify': _classify})
    return f'{redirect_url}?{parameters}'


def set_initial_value(_date, _classify, initial_value_dict):
    """
    支出データ入力部の初期値を設定する。
    :param _date: 支出データ入力欄の[日付]項目の初期値。
    :param _classify: 支出データ入力欄の[分類]項目の初期値。
    :param initial_value_dict: 初期値設定を格納するdictionaly変数。
    :return: なし。
    """
    initial_value_dict['date'] = _date
    initial_value_dict['classify'] = _classify


