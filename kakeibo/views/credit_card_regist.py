# 標準ライブラリ
from django.shortcuts import render
from io import TextIOWrapper
import csv

# 独自ライブラリ
from kakeibo.forms import YMForm, CardForm, CardFormSet
import kakeibo.util.kakeibo_util as util
import kakeibo.util.credit_card as cc
import mysite.util as base_util

'''
！！リファクタリングしたいこと！！
・セッションの共通化、セッションがどこまで有効かを定義
'''


def credit_card_regist(request):
    """
    カード支出登録画面を制御する。
    :param request: ブラウザから送信されたデータ
    :return: Templateに送るデータ
    """

    # 現在日時の取得
    dt_now = base_util.datetime.now()

    # カード支出明細の取得
    card_detail_master = util.カード支出明細.objects.filter(削除フラグ='0').order_by('id')
    card_detail_operation = util.CardDetailTableOperation(card_detail_master)

    # セッションデータの取得
    # セッション周りとかはいつか共通化したい。
    yyyymm = request.session['yyyymm'] if 'yyyymm' in request.session else dt_now.strftime('%Y%m')

    # 年月変更処理
    if request.method == 'POST':

        # requestデータとボタンを押したフォームの名前を取得。
        request_data = request.POST
        form_name = ''
        if 'form_name' in request_data:
            form_name = request_data.get('form_name')

        # 年月変更操作
        if form_name == 'trans_page':
            # 入力した値の取得。値の整形もしている。
            detail_form_data = YMForm(request_data)
            detail_form_data.is_valid()
            cleaned_data = detail_form_data.cleaned_data

            _yyyymm = cleaned_data.get('YYYYMM')

            # 移動ボタン押下時処理
            if 'change' in request_data:
                yyyymm = _yyyymm

            # 次月ボタン押下時処理
            if 'next' in request_data:
                yyyymm = base_util.calc_date(yyyymm, 0, 1, 0)

            # 前月ボタン押下時処理
            if 'back' in request_data:
                yyyymm = base_util.calc_date(yyyymm, 0, -1, 0)

        # クレジットカードデータのcsv取込
        if form_name == 'import_file':
            if 'import' in request_data:

                # ブラウザで入力したcsvファイルの取得
                file_data = TextIOWrapper(request.FILES['csvfile'].file, encoding='Shift_JIS')
                # csvデータを変数に格納
                csv_file = csv.DictReader(file_data)

                # csvデータをRakutenCardDataListに格納
                card_data_list_from_csv = cc.RakutenCardDataList()
                card_data_list_from_csv.set_csv_data(csv_file)

                # カード支出明細テーブルへのインサート
                card_detail_operation.ins_rows(yyyymm, card_data_list_from_csv)

        # 画面入力されたデータを更新する。
        if form_name == 'regist_card_data':
            if 'regist' in request_data:

                # 入力値チェック
                card_formset = CardFormSet(request_data)
                card_formset.is_valid()

                # updateデータの取得、更新
                upd_card_data_list_from_formset = get_card_data_list_from_formset(card_formset, UpdDelKubun.update)
                card_detail_operation.upd_rows(upd_card_data_list_from_formset)

                # 削除データの取得、削除
                del_card_data_list_from_formset = get_card_data_list_from_formset(card_formset, UpdDelKubun.delete)
                card_detail_operation.del_rows(del_card_data_list_from_formset)

    # 画面表示用にクレジットカードデータを取得
    card_detail_records = card_detail_operation.get_month_records(yyyymm)
    card_form_initial_data = get_card_formset_initial_data(card_detail_records)

    form_ymform = YMForm(initial={'YYYYMM': yyyymm})
    form_card_formset = CardFormSet(initial=card_form_initial_data)

    # セッションデータの登録
    request.session['yyyymm'] = yyyymm

    context = {
        'ymform': form_ymform,
        'card_formset': form_card_formset
    }

    return render(request, 'kakeibo/credit_card_regist.html', context)


def get_card_formset_initial_data(card_detail_records):
    """
    カード支出明細テーブルからカード支出登録フォームの表示データの取得
    :param card_detail_records: カード支出明細テーブルデータ
    :return: カード支出登録フォームの表示データ
    """
    result = []

    for card_detail_row in card_detail_records:
        card_detail_row: util.カード支出明細 = card_detail_row  # 型指定
        # noinspection PyUnresolvedReferences
        card_data_form = {
            'row_id': card_detail_row.id,  # 型指定するとidが警告になるため「noinspection」を実施
            'payment_month': card_detail_row.支払月,
            'use_date': card_detail_row.利用日,
            'shop_name': card_detail_row.利用店名,
            'money': card_detail_row.利用金額,
            'classify_person': '{0}_{1}'.format(str(card_detail_row.支出分類コード), str(card_detail_row.対象者コード)),
            'delete': False,
            'remarks': card_detail_row.備考,
        }

        result.append(card_data_form)

    return result


def get_card_data_list_from_formset(card_formset, is_upd_del):
    """
    画面入力データをRakutenCardDataListに格納して返す。
    :param card_formset: 画面入力データ
    :param is_upd_del: 更新データか削除データかどっちを取得するか判定するフラグ
    :return: RakutenCardDataListデータ
    """
    card_data_list = cc.RakutenCardDataList()

    for card_form in card_formset:
        card_form: CardForm = card_form.cleaned_data

        # 「支出分類_対象者」が入力されていれば取得、なければ空のリストを取得
        if card_form['classify_person'] != '':
            classify_person = str(card_form['classify_person']).split('_')
        else:
            classify_person = ['', '']

        # 更新データを設定
        card_data: cc.RakutenCardData = cc.RakutenCardData()
        card_data.table_id = card_form['row_id']
        card_data.classify_code = classify_person[0]
        card_data.person_code = classify_person[1]
        card_data.remarks = card_form['remarks']

        # 削除のチェックボックスが有効であるかを判定
        if card_form['delete'] == (not bool(is_upd_del)):
            card_data_list.set_row(card_data)

    return card_data_list


class UpdDelKubun:
    update = True
    delete = False
