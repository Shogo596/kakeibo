# 標準ライブラリ
from django.shortcuts import render
from datetime import datetime

# 独自ライブラリ
from kakeibo.models import 収入支出明細, 収入支出分類マスタ, 対象者マスタ, 定例支出マスタ
from kakeibo.forms import RegularFormSet, YMForm
import kakeibo.util.kakeibo_util as util
import mysite.util as base_util


def regist_regular_expense(request):

    # 画面表示する年月の取得
    if 'yyyymm' in request.session:
        yyyymm = request.session['yyyymm']
    else:
        dt_now = datetime.now()
        yyyymm = dt_now.strftime('%Y%m')

    # 年月変更処理
    if request.method == 'POST':

        # 入力した値の取得。値の整形もしている。
        request_data = request.POST
        detail_form_data = YMForm(request_data)
        detail_form_data.is_valid()
        cleaned_data = detail_form_data.cleaned_data

        _yyyymm = cleaned_data.get('yyyymm')

        # 移動ボタン押下時処理
        if 'change' in request.POST:
            yyyymm = _yyyymm

        # 次月ボタン押下時処理
        if 'next' in request.POST:
            yyyymm = base_util.Date.calc_date(yyyymm, 0, 1, 0)

        # 前月ボタン押下時処理
        if 'back' in request.POST:
            yyyymm = base_util.Date.calc_date(yyyymm, 0, -1, 0)

    # マスタデータと支出明細の取得
    classify_records = 収入支出分類マスタ.objects.filter(削除フラグ='0', 固定変動区分='0').order_by('表示順序')
    person_records = 対象者マスタ.objects.filter(削除フラグ='0').exclude(対象者コード='0000000000').order_by('表示順序')
    regular_records = 定例支出マスタ.objects.filter(削除フラグ='0', 開始年月__lte=yyyymm, 終了年月__gte=yyyymm)
    detail_records = 収入支出明細.objects\
        .filter(削除フラグ='0', 対象年月日__startswith=yyyymm, 収入支出分類コード__固定変動区分='0').order_by('id').reverse()

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
                date = cleaned_data.get('date')
                classify = cleaned_data.get('classify_code')
                person = cleaned_data.get('person_code')
                money = cleaned_data.get('money')

                # 登録時に使用する項目の設定
                name = ''
                tax = False

                # 収入支出明細への登録
                util.add_upd_detail_row(date, classify, person, name, money, tax, upd_flg='1')

        # 削除ボタン押下時処理
        if 'delete' in request.POST:
            # 画面表示している年月のデータを削除する。
            util.delete_table_rows(detail_records)

    # 画面表示用の定例支出データの取得
    regular_data_list = get_regular_data_list(classify_records, person_records, regular_records, detail_records, yyyymm)

    # Templateに送るデータの作成。
    context = {
        # 'regular_data_list': regular_data_list,
        'regular_data_list': RegularFormSet(initial=regular_data_list),
        'YMForm': YMForm(initial={'yyyymm': yyyymm}),
    }

    # 年月をセッションに登録
    request.session['yyyymm'] = yyyymm

    # 支出データ一覧画面の表示。"context"の内容をもとに"view_list.html"が表示される。
    # return render(request, 'kakeibo/view_list.html', context)
    return render(request, 'kakeibo/regist_regular_expense.html', context)


def get_regular_data_list(classify_records, person_records, regular_records, detail_records, yyyymm):
    """
    画面表示用の定例支出データの取得を返す。
    :param classify_records: 収入支出分類マスタ（固定変動区分＝固定費のみ）
    :param person_records: 対象者マスタ（対象者＝世帯全員は除く）
    :param regular_records: 定例支出マスタ
    :param detail_records: 収入支出明細テーブルの固定費データ（特定年月データかつ固定変動区分＝固定費）
    :param yyyymm: 対象年月
    :return: 画面表示用の定例支出データ（list型）
    """

    result = []

    for classify_row in classify_records:
        for person_row in person_records:

            # 画面表示する定例支出データの初期化
            regular_form_data = RegularFormData()
            regular_form_data.form_name = classify_row.収入支出分類名
            regular_form_data.date = yyyymm + '00'
            regular_form_data.classify = classify_row.収入支出分類コード
            regular_form_data.person = '0000000000'
            regular_form_data.money = 0

            # 対象者区別有無が"1"だったら一部編集
            person_umu_flg = classify_row.対象者区別有無
            if person_umu_flg == '1':
                regular_form_data.form_name = classify_row.収入支出分類名 + '（' + person_row.対象者名 + '）'
                regular_form_data.person = person_row.対象者コード

            # 対象の定例支出項目がすでに収入支出明細テーブルに存在する場合は取得。対象年月日と金額を取得する。
            detail_row = detail_records\
                .filter(収入支出分類コード=regular_form_data.classify, 対象者コード=regular_form_data.person).first()

            # 収入支出明細テーブルから行取得できたか判定。取得できたら以下取得。
            # できない場合、定例支出マスタにレコードがあれば金額を取得する。
            if detail_row is not None:
                regular_form_data.date = detail_row.対象年月日
                regular_form_data.money = detail_row.金額
            else:
                # 定例支出マスタから取得
                regular_rows = regular_records\
                    .filter(収入支出分類コード=regular_form_data.classify, 対象者コード=regular_form_data.person)

                # 定例支出マスタに複数金額が存在する場合はすべて合算。
                for regular_row in regular_rows:

                    # 有効月のチェックをして対象であれば金額を取得。
                    int_mm = int(yyyymm[4:])
                    if regular_row.有効月[int_mm - 1] == '1':
                        regular_form_data.money += regular_row.金額

            # 画面初期表示用にハッシュ化してListに突っ込む。
            regular_data = {
                'form_name': regular_form_data.form_name,
                'date': regular_form_data.date,
                'classify_code': regular_form_data.classify,
                'person_code': regular_form_data.person,
                'money': regular_form_data.money
            }
            result.append(regular_data)

            # 対象者区別有無が'1'じゃない場合は対象者が"世帯全員"のみなので対象者レコードのループは終わり。
            if person_umu_flg != '1':
                break

    return result


class RegularFormData:
    form_name = ''
    date = ''
    classify_code = ''
    person_code = ''
    money = 0
