from django.shortcuts import render, redirect
from kakeibo.models import 支出明細, 支出分類マスタ
from kakeibo.forms import DetailForm
# from django.utils import timezone
from urllib.parse import urlencode

# 定数
VIEW_LIST_URL = '/kakeibo/view_list/'
TAX = 1.1


def view_list(request):
    """
    支出データ一覧画面のメインメソッド。表示内容のデータを作成、編集する。
    :param request: お作法。ブラウザから送信されたリクエストデータが格納されている。
    :return: なし。このメソッドの実行後、Templateにより画面表示される。
    """

    # 支出明細の取得。支出データ一覧部の表示に利用する。
    # details = 支出明細.objects.order_by('id').reverse()[:20]
    # details = details.reverse()[:20]
    # details = 支出明細.objects.filter(削除フラグ='0', 支出分類マスタ__固定変動区分='1').order_by('id').reverse().select_related()
    details = 支出明細.objects.filter(削除フラグ='0', 支出分類コード__固定変動区分='1').order_by('id').reverse()

    # 支出データ入力欄の初期値設定の初期化。
    initial_value_dict = {
        'date': '',
        'classify': '',
    }

    # リクエストメソッドがGETの場合。
    # 初期表示の場合か、支出データの追加登録後にリダイレクトにて表示される場合が対象。
    if request.method == 'GET':
        data = request.GET  # 画面入力されたデータ

        date = data.get('date')
        classify = data.get('classify')

        # GETリクエストとして初期値が設定されている場合。（リダイレクトされてきた場合）
        if date is not None and classify is not None:
            set_initial_value(date, classify, initial_value_dict)

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
        name = cleaned_data.get('name')
        money = cleaned_data.get('money')
        is_tax = cleaned_data.get('tax')

        # 削除時に使用する項目
        row_id = request_data.get('id')

        if 'add' in request_data:
            add_detail_row(date, classify, name, money, is_tax)

        elif 'delete' in request_data:
            delete_detail_row(row_id)

        redirect_url = get_url_view_list(date, classify)
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


def add_detail_row(date, classify, name, money, is_tax):
    """
    支出明細テーブルに画面入力された支出データを登録する。
    :param date: 対象年月日
    :param classify: 支出分類コード
    :param name: 項目名
    :param money: 金額
    :param is_tax: 税込計算するかどうか
    :return: なし。
    """
    # DB的には日付は数値8桁のため整形。
    str_date = date.strftime('%Y%m%d')

    # 税込計算。入力された金額に税額を加える。
    if is_tax is True:
        money = money * TAX

    支出明細.objects.create(
        対象年月日=str_date,
        支出分類コード=支出分類マスタ.objects.get(支出分類コード=classify),
        項目名=name,
        金額=money,
    )


def delete_detail_row(row_id):
    """
    支出明細テーブルから支出データレコードを削除する。実態は削除フラグを"1"に更新しているだけ。
    :param row_id: 削除ボタン押下時の行番号。
    :return: なし。
    """
    # 物理削除はやめた。
    # detail_id = data['id']
    # 支出明細.objects.filter(id=detail_id).delete()

    # 削除フラグを更新する。
    detail_row = 支出明細.objects.filter(id=row_id).first()
    detail_row.削除フラグ = '1'
    detail_row.save()


def get_url_view_list(date, classify):
    """
    支出データ一覧画面のURLを取得する。引数に値が存在する場合はGETリクエストとしてパラメータを設定する。
    :param date: 支出データ入力欄の[日付]項目の初期値。初期値を表示する場合のみ設定。
    :param classify: 支出データ入力欄の[分類]項目の初期値。初期値を表示する場合のみ設定。
    :return: 支出データ一覧画面のURL。
    """
    redirect_url = VIEW_LIST_URL

    if date is None and classify is None:
        return redirect_url

    # GETリクエストとしてURLを作成する。
    parameters = urlencode({'date': date, 'classify': classify})
    return f'{redirect_url}?{parameters}'


def set_initial_value(date, classify, initial_value_dict):
    """
    支出データ入力部の初期値を設定する。
    :param date: 支出データ入力欄の[日付]項目の初期値。
    :param classify: 支出データ入力欄の[分類]項目の初期値。
    :param initial_value_dict: 初期値設定を格納するdictionaly変数。
    :return: なし。
    """
    initial_value_dict['date'] = date
    initial_value_dict['classify'] = classify


