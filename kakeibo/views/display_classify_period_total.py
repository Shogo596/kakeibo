# 標準ライブラリ
from django.shortcuts import render
from collections import defaultdict

# 独自ライブラリ
from kakeibo.forms import YMForm
import mysite.util as base_util
import kakeibo.util.sql_operation as sql_ope


def display_classify_period_total(request):
    """
    特定の期間の収支を棒グラフと折れ線グラフで表示する。
    :param request: ブラウザからの入力データ
    :return: ブラウザ表示内容
    """

    # 現在日時の取得
    dt_now = base_util.datetime.now()
    # 4年前日付の取得
    dt_year_ago = dt_now + base_util.relativedelta.relativedelta(years=-1)

    # セッションデータの初期化。自画面遷移でなければ初期化する。
    if ('HTTP_REFERER' not in request.META) or ('display_classify_period_total' not in request.META['HTTP_REFERER']):
        request.session.clear()

    # セッションデータの取得
    # ！！セッション周りとかはいつか共通化したい。！！
    yyyymm = request.session['yyyymm'] if 'yyyymm' in request.session else dt_year_ago.strftime('%Y') + '01'
    period = request.session['period'] if 'period' in request.session else 12
    interval = request.session['interval'] if 'interval' in request.session else 1

    # 年月変更処理
    if request.method == 'POST':

        # requestデータとボタンを押したフォームの名前を取得。
        request_data = request.POST
        form_name = ''
        if 'form_name' in request_data:
            form_name = request_data.get('form_name')

        # 年月変更操作
        if form_name == 'trans_page':
            # フォームデータの編集。formsの変数に格納している。
            result_ymform: YMForm = get_ymform_data(request_data)

            # 各フォーム値の取得
            changed_yyyymm = result_ymform.data.get('yyyymm')
            yyyymm = changed_yyyymm if changed_yyyymm is not None else yyyymm
            changed_period = result_ymform.data.get('period')
            period = changed_period if changed_period is not None else period
            changed_interval = result_ymform.data.get('interval')
            interval = changed_interval if changed_interval is not None else interval

    # 収支データの取得
    display_records = get_display_records(yyyymm, period, '1')

    # 収支データをlist型からdict型に変換する。
    display_dict = change_dict_from_display_records(display_records)

    # 画面表示データの作成
    line_chart_data = LineChartData()
    # line_chart_data.set_test_data()
    line_chart_data.set_label()
    line_chart_data.set_y_axis(interval)
    line_chart_data.set_data(yyyymm, period, interval, display_dict)

    # フォーム内容の取得
    form_ymform = YMForm(initial={'yyyymm': yyyymm, 'period': period, 'interval': interval})

    # セッションデータの登録
    request.session['yyyymm'] = yyyymm
    request.session['period'] = period
    request.session['interval'] = interval

    # Templateへの送信データの作成
    context = {
        'ymform': form_ymform,
        'line_chart_data': line_chart_data,
    }

    return render(request, 'kakeibo/display_classify_period_total.html', context)


def get_ymform_data(request_data):
    """
    日付によるページ更新部を処理する。入力された年月と期間を取得する。
    :param request_data: ブラウザから入力された値
    :return: 年月と期間
    """
    # 入力値の整形。
    ymform_data = YMForm(request_data)
    ymform_data.is_valid()
    cleaned_data = ymform_data.cleaned_data

    # 入力した値の取得。
    wk_yyyymm = cleaned_data.get('yyyymm')
    wk_period = cleaned_data.get('period')
    wk_interval = cleaned_data.get('interval')

    # 入力値を正しく格納。
    yyyymm = wk_yyyymm
    period = int(wk_period) if wk_period is not None else 1
    interval = int(wk_interval) if wk_interval is not None else 1

    # 変更ボタン押下時処理
    if 'change' in request_data:
        pass

    # 次ボタン押下時処理
    if 'next' in request_data:
        if interval == YMForm.year:
            yyyymm = base_util.Date.calc_date(yyyymm, 1, 0, 0)
        else:
            yyyymm = base_util.Date.calc_date(yyyymm, 0, 1, 0)

    # 前ボタン押下時処理
    if 'back' in request_data:
        if interval == YMForm.year:
            yyyymm = base_util.Date.calc_date(yyyymm, -1, 0, 0)
        else:
            yyyymm = base_util.Date.calc_date(yyyymm, 0, -1, 0)

    # 計算した結果をFormに格納
    return_ymform = YMForm()
    return_ymform.data['yyyymm'] = yyyymm
    return_ymform.data['period'] = period
    return_ymform.data['interval'] = interval

    return return_ymform


def get_display_records(yyyymm, period, in_out_kubun):
    """
    DBから収入もしくは支出データを取得する。
    :param yyyymm: 取得対象の年月
    :param period: 取得対象の期間
    :param in_out_kubun: 収入支出区分
    :return: 取得した支出データをlist型で返す。
    """
    # 収支データの取得
    sql = sql_ope.PeriodClassifyInoutMoney()
    kotei_hendo_kubun = '0,1'
    start_ym = yyyymm
    end_ym = base_util.Date.calc_date(start_ym, 0, period - 1, 0)
    sql.set_params(start_ym, end_ym, in_out_kubun, kotei_hendo_kubun)
    display_records = sql.execute()

    return display_records


def change_dict_from_display_records(display_records: list) -> dict:
    """
    list型の収支データをdict型に変換する。
    :param display_records: list型の収支データ
    :return: dict型の収支データ
    """
    result = defaultdict(lambda : defaultdict(int))
    for row in display_records:
        key_classify = row['収入支出分類名']
        key_ym = row['対象年月']
        value = int(row['合計金額'])
        result[key_classify][key_ym] = value
    return result


class LineChartData:
    """
    棒グラフ・折れ線グラフの表示に使うクラス。
    以下の変数に値を格納すれば各グラフが表示可能。
    """
    def __init__(self):
        """
        クラス変数の初期化
        """
        # 全体的な表示設定
        self.title = ''
        self.labels = []  # strデータを入れる
        # 折れ線グラフのY軸設定
        self.lineMax = 0
        self.lineMin = 0
        self.lineStepSize = 0
        # 収支差額の折れ線グラフ設定
        self.lineNames = []
        self.lineDatasets = []

    def set_label(self):
        """
        ラベル系データのセット
        """
        self.title = '分類期間収支データ'

    def set_y_axis(self, interval):
        """
        Y軸に利用するデータのセット。画面表示する間隔が1月か1年かでY軸のデータも調整する。
        :param interval: 画面表示する間隔
        """
        if interval == YMForm.year:
            self._set_y_axis_year()
        else:
            self._set_y_axis_month()

    def _set_y_axis_month(self):
        """
        1月表示用のY軸データ
        """
        self.lineMax = 100000
        self.lineMin = 0
        self.lineStepSize = 10000

    def _set_y_axis_year(self):
        """
        1年表示用のY軸データ
        """
        self.lineMax = 1000000
        self.lineMin = 0
        self.lineStepSize = 100000

    def set_data(self, date, period, interval, display_dict: dict):
        """
        画面表示する棒グラフと折れ線グラフのデータのセット
        :param date: 表示開始年月
        :param period: 表示期間
        :param interval: 表示間隔
        :param display_dict: 終始データのdict
        """
        label_add_flg = True
        for classify_name in display_dict.keys():
            inout_arr = []
            for i in range(0, period, interval):
                wk_date = base_util.Date.calc_date(date, 0, i, 0)
                inout = self._get_sum(classify_name, wk_date, interval, display_dict)
                inout_arr.append(inout)
                # labelの設定は1回だけでいいのでフラグで管理する。
                if label_add_flg:
                    self.labels.append(base_util.Date.add_slash(wk_date))

            self.lineNames.append(classify_name)
            self.lineDatasets.append(inout_arr)
            label_add_flg = False

    @staticmethod
    def _get_sum(classify, date, count, display_dict: dict):
        """
        引数の年月、期間の金額の合計値を返す。
        :param date: 対象年月
        :param count: 対象期間
        :param display_dict: 合計値が格納されているdict。中身の「key=yyyymm, value=money」の形。
        :return: 合計金額
        """
        sum_money = 0
        for i in range(count):
            wk_date = base_util.Date.calc_date(date, 0, i, 0)
            money: int = int(display_dict[classify][wk_date]) if wk_date in display_dict[classify] else 0
            sum_money += money
        return sum_money

    def set_test_data(self):
        """
        動作確認用データ
        """
        self.title = 'テストデータ'
        self.labels = ['2018/01', '2018/02', '2018/03', '2018/04', '2018/05', '2018/06', '2018/07']
        self.lineMax = 300000
        self.lineMin = 0
        self.lineStepSize = 100000
        self.lineNames = ['折れ線A', '折れ線B']
        self.lineDatasets = [
            [100000, 110000, 150000, 120000, 90000, 120000, 130000],
            [200000, 210000, 250000, 220000, 190000, 220000, 230000],
            ]
