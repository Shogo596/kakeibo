# 標準ライブラリ
from django.shortcuts import render
from datetime import datetime

# 独自ライブラリ
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
    classify_records = util.収入支出分類マスタ.objects.filter(削除フラグ='0', 固定変動区分='0').order_by('表示順序')
    person_records = util.対象者マスタ.objects.filter(削除フラグ='0').exclude(対象者コード='0000000000').order_by('表示順序')
    regular_records = util.定例支出マスタ.objects.filter(削除フラグ='0', 開始年月__lte=yyyymm, 終了年月__gte=yyyymm)
    inout_detail_records = util.収入支出明細.objects\
        .filter(削除フラグ='0', 対象年月日__startswith=yyyymm, 収入支出分類コード__固定変動区分='0').order_by('id').reverse()
    inout_detail_operation = util.InoutDetailTableOperation(inout_detail_records)
    card_detail_master = util.カード支出明細.objects.filter(削除フラグ='0', 支払月=yyyymm).order_by('id')
    card_detail_operation = util.CardDetailTableOperation(card_detail_master)

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
                money_disabled = cleaned_data.get('money_disabled')

                # 登録時に使用する項目の設定
                name = ''
                tax = False

                # 収入支出明細への登録。disabled項目（カード支出明細に登録されているデータ）は登録しない。
                if money_disabled != '1':
                    inout_detail_operation.add_upd_row(None, date, classify, person, name, money, tax)

        # 削除ボタン押下時処理
        if 'delete' in request.POST:
            # 画面表示している年月のデータを削除する。
            inout_detail_operation.del_all()

    # 画面表示用の定例支出データの取得
    regular_data_list = get_regular_data_list(classify_records, person_records, regular_records, inout_detail_operation,
                                              card_detail_operation, yyyymm)

    # Templateに送るデータの作成。
    regular_formset = RegularFormSet(initial=regular_data_list)
    regular_formset = base_util.FormSet.set_disabled(regular_formset, 'money')
    context = {
        # 'regular_data_list': regular_data_list,
        'regular_data_list': regular_formset,
        'YMForm': YMForm(initial={'yyyymm': yyyymm}),
    }

    # 年月をセッションに登録
    request.session['yyyymm'] = yyyymm

    # 支出データ一覧画面の表示。"context"の内容をもとに"view_list.html"が表示される。
    # return render(request, 'kakeibo/view_list.html', context)
    return render(request, 'kakeibo/regist_regular_expense.html', context)


def get_regular_data_list(classify_records, person_records, regular_records, inout_detail_operation,
                          card_detail_operation, yyyymm):
    """
    画面表示用の定例支出データの取得を返す。
    :param classify_records: 収入支出分類マスタ（固定変動区分＝固定費のみ）
    :param person_records: 対象者マスタ（対象者＝世帯全員は除く）
    :param regular_records: 定例支出マスタ
    :param inout_detail_operation: 収入支出明細テーブルの固定費操作Obj
    :param card_detail_operation: カード支出明細テーブルの操作Obj
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
            regular_form_data.money_disabled = '0'

            # 対象者区別有無が"1"だったら一部編集
            person_umu_flg = classify_row.対象者区別有無
            if person_umu_flg == '1':
                regular_form_data.form_name = classify_row.収入支出分類名 + '（' + person_row.対象者名 + '）'
                regular_form_data.person = person_row.対象者コード

            # データ取得のフィルタ条件
            filter_dict = {'収入支出分類コード': regular_form_data.classify, '対象者コード': regular_form_data.person}

            # 対象の定例支出項目がすでに収入支出明細テーブルに存在する場合は取得。
            detail_rows = inout_detail_operation.get_row_filter(filter_dict)
            # カード支出明細（クレジットカード）のデータがあれば取得する。
            card_detail_rows = card_detail_operation.get_row_filter(filter_dict)

            # 収入支出明細テーブルから行取得できたか判定。取得できていたらそれを表示。
            # この画面から登録していないデータが存在する場合は画面をグレーアウトして更新不可にする。
            # 取得できなかった場合は定例支出マスタにレコードがあれば金額を取得する。
            is_registed = False  # 画面表示するデータがすでにテーブルに登録されているか。以下の処理で判定する。

            # 収入支出明細からデータを取得
            for detail_row in detail_rows:
                is_registed = True
                regular_form_data.money += detail_row.金額
                # 年月日の末尾2桁が"00"でなければこの画面で登録したデータでないためグレーアウトする。
                if not detail_row.対象年月日[6:] == '00':
                    regular_form_data.money_disabled = '1'

            # カード支出明細からデータを取得。
            for card_detail_row in card_detail_rows:
                is_registed = True
                regular_form_data.money += card_detail_row.利用金額
                # カード支出明細から登録したデータなのでグレーアウトする。
                regular_form_data.money_disabled = '1'

            # 上記でデータが取得できなかった場合は定例支出マスタからデフォルト値を取得する。
            if not is_registed:
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
                'money': regular_form_data.money,
                'money_disabled': regular_form_data.money_disabled,
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
    money_disabled = ''
