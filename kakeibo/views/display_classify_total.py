# 標準ライブラリ
from django.shortcuts import render

# 独自ライブラリ
from kakeibo.forms import YMForm, InOutCheckForm
import mysite.util as base_util
import kakeibo.util.sql_operation as sql_ope


def display_classify_total(request):
    """
    特定の期間の収支を円グラフ表示する。
    :param request: ブラウザからの入力データ
    :return: 円グラフ表示内容
    """

    # 現在日時の取得
    dt_now = base_util.datetime.now()

    # セッションデータの初期化。自画面遷移でなければ初期化する。
    if ('HTTP_REFERER' not in request.META) or ('display_classify_total' not in request.META['HTTP_REFERER']):
        request.session.clear()

    # セッションデータの取得
    # ！！セッション周りとかはいつか共通化したい。！！
    yyyymm = request.session['yyyymm'] if 'yyyymm' in request.session else dt_now.strftime('%Y%m')
    period = request.session['period'] if 'period' in request.session else 1
    # ↓円グラフ表示対象の"収入支出区分_固定変動区分"
    inout_check_list = request.session['inout'] if 'inout' in request.session else ['1_0', '1_1']

    # 年月変更処理
    if request.method == 'POST':

        # requestデータとボタンを押したフォームの名前を取得。
        request_data = request.POST
        form_name = ''
        if 'form_name' in request_data:
            form_name = request_data.get('form_name')

        # 年月変更操作
        if form_name == 'trans_page':
            result_ymform: YMForm = get_ymform_data(request_data)
            changed_yyyymm = result_ymform.data.get('yyyymm')
            yyyymm = changed_yyyymm if changed_yyyymm is not None else yyyymm
            changed_period = result_ymform.data.get('period')
            period = changed_period if changed_period is not None else period

        # 収支のチェックボックスの内容を取得
        if form_name == 'change_inout':
            inout_check_form_data = InOutCheckForm(request_data)
            inout_check_form_data.is_valid()
            cleaned_data = inout_check_form_data.cleaned_data
            inout_check_list = cleaned_data.get('check')

    # 収支データの取得
    display_records = []
    start_ym = yyyymm
    end_ym = base_util.Date.calc_date(start_ym, 0, period - 1, 0)
    for data in inout_check_list:
        check = str(data).split('_')
        sql = sql_ope.MonthlyInoutMoney(start_ym, end_ym, check[0], check[1])
        detail_records = sql.execute()
        display_records += detail_records

    # 画面表示データの作成
    pie_chart_data = PieChartData()
    pie_chart_data.title = '収支内訳'
    pie_chart_data.labels = [row['収入支出分類名'] for row in display_records]
    pie_chart_data.data = [int(row['合計金額']) for row in display_records]

    # フォーム内容の取得
    form_ymform = YMForm(initial={'yyyymm': yyyymm, 'period': period})
    form_inout_check_form = InOutCheckForm(initial={'check': inout_check_list})
    # form_card_formset = CardFormSet(initial=card_form_initial_data)

    # セッションデータの登録
    request.session['yyyymm'] = yyyymm
    request.session['period'] = period
    request.session['inout'] = inout_check_list

    # Templateへの送信データの作成
    context = {
        'ymform': form_ymform,
        'pie_chart_data': pie_chart_data,
        'inout_check_form': form_inout_check_form,
    }

    return render(request, 'kakeibo/display_classify_total.html', context)


def get_ymform_data(request_data):
    """
    日付によるページ更新部を処理する。入力された年月と期間を取得する。
    :param request_data: ブラウザから入力された値
    :return: 年月と期間
    """
    # 入力した値の取得。値の整形もしている。
    ymform_data = YMForm(request_data)
    ymform_data.is_valid()
    cleaned_data = ymform_data.cleaned_data

    yyyymm = cleaned_data.get('yyyymm')
    period = cleaned_data.get('period')

    # 変更ボタン押下時処理
    if 'change' in request_data:
        pass

    # 次月ボタン押下時処理
    if 'next' in request_data:
        yyyymm = base_util.Date.calc_date(yyyymm, 0, 1, 0)

    # 前月ボタン押下時処理
    if 'back' in request_data:
        yyyymm = base_util.Date.calc_date(yyyymm, 0, -1, 0)

    # 計算した結果をFormに格納
    return_ymform = YMForm()
    return_ymform.data['yyyymm'] = yyyymm
    return_ymform.data['period'] = period

    return return_ymform


class PieChartData:
    """
    円グラフの表示に使うクラス。
    以下の変数に値を格納すれば円グラフが表示可能。
    """
    title = 'タイトル'
    labels = ['A型', 'O型', 'B型', 'AB型']
    data = [38, 31, 21, 10]
