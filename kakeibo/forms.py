from django import forms
# from models import 収入支出分類マスタ, 対象者マスタ
# from django.contrib.admin.widgets import AdminDateWidget
import bootstrap_datepicker_plus as datetimepicker
import kakeibo.util.kakeibo_util as util

# 定数
# 「"収入支出区分_固定変動区分", 表示名称」で収支選択用のリスト作成
# アンダーバーを挟んで左が収入支出区分、右が固定変動区分
CHOICE = [
    ('0_0', '収入'),
    ('1_0', '支出（固定費）'),
    ('1_1', '支出（変動費）'),
]


######################################################
# ◆ファイル説明
# 入力フォームの形式や値を管理。
######################################################


class DetailForm(forms.Form):
    """
    日ごとの支出データの入力欄の管理。
    以下、特筆すべき項目の説明。
    日付：カレンダー入力させる。
    分類：支出分類マスタと対象者マスタの項目からプルダウンにて入力させる。
    """
    # 支出分類マスタからプルダウン用のリストを作成。
    # classify_list = []
    # for object in 収入支出分類マスタ.objects.filter(削除フラグ='0', 固定変動区分='1').order_by('表示順序'):
    #     classify_list.append((object.収入支出分類コード, object.収入支出分類名))

    # 対象者マスタからプルダウン用のリストを作成。
    # person_list = []
    # for object in 対象者マスタ.objects.filter(削除フラグ='0').exclude(対象者コード='0000000000').order_by('表示順序'):
    #     person_list.append((object.対象者コード, object.対象者名))

    row_id = forms.IntegerField(label='行番号', required=False, widget=forms.HiddenInput())
    # 日付項目は"datetimepicker"を利用してカレンダー入力を可能とする。
    # date = forms.CharField(label='日付')
    date = forms.CharField(widget=datetimepicker.DatePickerInput(
        format='%Y%m%d',
        options={
            'locale': 'ja',
            'dayViewHeaderFormat': 'YYYY年 MMMM',
        },
        attrs={'autofocus': 'autofocus'}
    ), label='日付')
    # classify = forms.ChoiceField(label='分類', widget=forms.Select, choices=classify_list)
    # person = forms.ChoiceField(label='対象者', widget=forms.Select, choices=person_list)
    classify_person = forms.ChoiceField(label='分類', required=False, widget=forms.Select)  # プルダウンの中身はinitで作成。
    name = forms.CharField(label='項目名', max_length=100)
    money = forms.IntegerField(label='金額')
    is_tax = forms.BooleanField(label='税', required=False, widget=forms.CheckboxInput())

    def __init__(self, *args, **kwargs):
        """
        初期設定。項目「分類」の設定を行う。
        :param args:
        :param kwargs:
        """

        # Viewの引数から送られた独自データを取得する。
        self.inout_value_dict: dict = kwargs.pop('inout_value_dict', {})
        inout_kubun = self.inout_value_dict.get('inout_kubun', '1')
        kotei_hendo_kubun = self.inout_value_dict.get('kotei_hendo_kubun', '1')

        # 本来のinitを実行する。定型文。
        super(DetailForm, self).__init__(*args, **kwargs)

        # 「収入支出分類_対象者」のプルダウンを作成、設定する。
        classify_person_combobox = util.ClassifyPersonOpe.get_classify_person_combobox(inout_kubun, kotei_hendo_kubun,
                                                                                       False)
        self.fields['classify_person'].choices = classify_person_combobox
        self.fields['date'].widget = datetimepicker.DatePickerInput(
            format='%Y%m%d',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            },
            attrs={'autofocus': 'autofocus'}
        )


class RegularForm(forms.Form):
    """
    例月支出データの表示フォーム
    """
    row_id = forms.IntegerField(label='行番号', required=False, widget=forms.HiddenInput())
    form_name = forms.CharField(label='フォーム名', required=False)
    date = forms.CharField(max_length=8, label='対象年月日', required=False, widget=forms.HiddenInput())
    classify_code = forms.CharField(max_length=10, label='収入支出分類コード', required=False, widget=forms.HiddenInput())
    person_code = forms.CharField(max_length=10, label='対象者コード', required=False, widget=forms.HiddenInput())
    money = forms.IntegerField(label='金額')
    # エラーチェック用
    money_define = forms.IntegerField(label='デフォルト金額', required=False, widget=forms.HiddenInput())
    # 値が'1'の場合は「金額」項目をdisabledにする。
    money_disabled = forms.CharField(max_length=1, label='金額非表示有無', required=False, widget=forms.HiddenInput())


RegularFormSet = forms.formset_factory(RegularForm, extra=0)


class YMForm(forms.Form):
    """
    年月遷移用のフォーム
    """
    month = 1
    year = 12
    month_or_year_list = [
        (month, '１月'),
        (year, '１年'),
    ]
    yyyymm = forms.CharField(label='年月', max_length=6, widget=forms.TextInput(attrs={'size': 6}))
    period = forms.IntegerField(label='期間', widget=forms.TextInput(attrs={'size': 2}))
    interval = forms.ChoiceField(label='分類', widget=forms.Select, choices=month_or_year_list)


class InOutCheckForm(forms.Form):
    """
    収支の表示を制御するマルチチェックボックスのフォーム
    """
    check = forms.MultipleChoiceField(label='収支表示内容', choices=CHOICE, required=True,
                                      widget=forms.CheckboxSelectMultiple(attrs={"onChange": 'submit();',
                                                                                 "id": 'check', })
                                      )


class InOutRadioForm(forms.Form):
    """
    収支の表示を制御するラジオボタンのフォーム
    """
    check = forms.ChoiceField(label='分類制御', choices=CHOICE, required=True,
                              widget=forms.RadioSelect(attrs={"onChange": 'submit();', "id": 'check', })
                              )


class CardForm(forms.Form):
    """
    カード支出データ表示用のフォーム
    """
    classify_person_combobox = util.ClassifyPersonOpe.get_classify_person_combobox('1', '', True)

    row_id = forms.IntegerField(label='行番号', required=False, widget=forms.HiddenInput())
    payment_month = forms.CharField(label='支払月', max_length=6, required=False, widget=forms.HiddenInput())
    use_date = forms.CharField(label='利用年月日', max_length=8, required=False, widget=forms.HiddenInput())
    shop_name = forms.CharField(label='店名', max_length=100, required=False, widget=forms.HiddenInput())
    money = forms.IntegerField(label='金額', required=False, widget=forms.HiddenInput())
    # memo:↓必須制御をかけると画面から取得した場合にkey errorになる。
    classify_person = forms.ChoiceField(label='支出分類_対象者',
                                        required=False, widget=forms.Select, choices=classify_person_combobox)
    remarks = forms.CharField(label='収入支出分類コード', max_length=100, required=False)
    delete = forms.BooleanField(label='削除', required=False, widget=forms.CheckboxInput())


CardFormSet = forms.formset_factory(CardForm, extra=0)


class ViewSearchForm(forms.Form):
    """
    一覧画面の表示条件用のフォーム
    """
    date_start = forms.CharField(label='開始日', max_length=8, required=False,
                                 widget=datetimepicker.DatePickerInput(
                                    format='%Y%m%d',
                                    options={
                                        'locale': 'ja',
                                        'dayViewHeaderFormat': 'YYYY年 MMMM',
                                    },
                                 )
                                 )
    date_end = forms.CharField(label='終了日', initial='', max_length=8, required=False,
                               widget=datetimepicker.DatePickerInput(
                                   format='%Y%m%d',
                                   options={
                                       'locale': 'ja',
                                       'dayViewHeaderFormat': 'YYYY年 MMMM',
                                   },
                               )
                               )
    check = forms.ChoiceField(label='収支区分', choices=CHOICE, required=True,
                              widget=forms.RadioSelect(attrs={"id": 'check', })
                              )
    name = forms.CharField(label='項目名', max_length=100, required=False)
    money_min = forms.IntegerField(label='下限額', required=False)
    money_max = forms.IntegerField(label='上限額', required=False)
    row_count = forms.IntegerField(label='表示行数', required=True)
