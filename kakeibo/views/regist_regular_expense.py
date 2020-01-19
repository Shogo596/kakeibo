from django.shortcuts import render, redirect
from kakeibo.models import 支出明細, 支出分類マスタ, 対象者マスタ
from kakeibo.forms import RegularForm, RegularFormSet
import datetime


def regist_regular_expense(request):

    ym = '202001'
    date = ym + '00'

    classify_records = 支出分類マスタ.objects.filter(削除フラグ='0', 固定変動区分='0').order_by('表示順序')
    person_records = 対象者マスタ.objects.filter(削除フラグ='0').exclude(対象者コード='0000000000').order_by('表示順序')
    regular_records = 支出明細.objects.filter(削除フラグ='0', 対象年月日=date, 支出分類コード__固定変動区分='0').order_by('id').reverse()

    if request.method == 'POST':

        # 登録ボタン押下時処理
        if 'regist' in request.POST:

            # 入力した値の取得。
            regular_formset = RegularFormSet(request.POST)
            regular_formset.is_valid()

            for regular_form in regular_formset:
                # 値の整形。
                cleaned_data = regular_form.cleaned_data

                # 登録時に使用する項目の取得
                classify = cleaned_data.get('classify_code')
                person = cleaned_data.get('person_code')
                money = cleaned_data.get('money')

                # 登録時に使用する項目の設定
                name = ''
                date = date  # dateはもっと上で定義
                tax = False

                # 支出明細への登録
                add_upd_detail_row(date, classify, person, name, money, tax)
                break

    # 画面表示用の定例支出データの取得
    regular_data_list = get_regular_data_list(classify_records, person_records, regular_records)

    # Templateに送るデータの作成。
    context = {
        # 'regular_data_list': regular_data_list,
        'regular_data_list': RegularFormSet(initial=regular_data_list),
    }

    # 支出データ一覧画面の表示。"context"の内容をもとに"view_list.html"が表示される。
    # return render(request, 'kakeibo/view_list.html', context)
    return render(request, 'kakeibo/regist_regular_expense.html', context)


def get_regular_data_list(classify_records, person_records, regular_records):
    """
    画面表示用の定例支出データの取得を返す。
    :param classify_records: 支出分類マスタ（固定変動区分＝固定費のみ）
    :param person_records: 対象者マスタ（対象者＝世帯全員は除く）
    :param regular_records: 支出明細テーブルの固定費データ（特定年月データかつ固定変動区分＝固定費）
    :return: 画面表示用の定例支出データ（list型）
    """

    result = []

    for classify_row in classify_records:
        for person_row in person_records:

            regular_data = {
                'form_name': '',
                'classify_code': '',
                'person_code': '',
                'money': 0,
            }

            if classify_row.対象者区別有無 != '1':
                regular_data['form_name'] = classify_row.支出分類名
                regular_data['classify_code'] = classify_row.支出分類コード
                regular_data['person_code'] = '0000000000'
                regular_data['money'] = get_detail_money(regular_records, classify_row.支出分類コード, '0000000000', '')

                result.append(regular_data)
                break

            regular_data['form_name'] = classify_row.支出分類名 + '（' + person_row.対象者名 + '）'
            regular_data['classify_code'] = classify_row.支出分類コード
            regular_data['person_code'] = person_row.対象者コード
            regular_data['money'] = get_detail_money(regular_records, classify_row.支出分類コード, person_row.対象者コード, '')

            result.append(regular_data)

    return result


def get_detail_money(regular_records, classify, person, name):
    """
    支出明細テーブルから金額を取得する。
    :param classify: 支出分類コード
    :param person: 対象者コード
    :param name: 項目名
    :return: 上記パラメータに紐づく明細データの金額
    """

    # 支出明細テーブルから取得
    detail_row = regular_records.filter(支出分類コード=classify, 対象者コード=person, 項目名=name).first()

    # 行取得できたか判定
    money = 0
    if detail_row is not None:
        money = detail_row.金額

    return money


def add_upd_detail_row(date, classify, person, name, money, is_tax):
    """
    支出明細テーブルに支出データを更新する。
    :param date: 対象年月日
    :param classify: 支出分類コード
    :param person: 対象者コード
    :param name: 項目名
    :param money: 金額
    :param is_tax: 税込計算するかどうか
    :return: なし。
    """
    # 税込計算。入力された金額に税額を加える。
    if is_tax is True:
        money = money * 1.1

    # defaults以外をキーとして、データがあればINSERT、データがなければdefaultで値を更新する。
    支出明細.objects.update_or_create(
        対象年月日=date,
        支出分類コード=支出分類マスタ.objects.get(支出分類コード=classify),
        対象者コード=対象者マスタ.objects.get(対象者コード=person),
        項目名=name,
        defaults={
            '金額': money,
        },
    )

