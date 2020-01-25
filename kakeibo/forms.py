from django import forms
from .models import 支出基本, 支出明細, 支出分類マスタ, 対象者マスタ
# from django.contrib.admin.widgets import AdminDateWidget
import bootstrap_datepicker_plus as datetimepicker


######################################################
# ◆ファイル説明
# 入力フォームの形式や値を管理。
######################################################


class DetailForm(forms.Form):
    """
    日ごとの支出データの入力欄の管理。
    以下、特筆すべき項目の説明。
    日付：カレンダー入力させる。
    分類：支出分類マスタの項目からプルダウンにて入力させる。
    """
    # 支出分類マスタからプルダウン用のリストを作成。
    classify_list = []
    for object in 支出分類マスタ.objects.filter(削除フラグ='0', 固定変動区分='1').order_by('表示順序'):
        classify_list.append((object.支出分類コード, object.支出分類名))

    # 対象者マスタからプルダウン用のリストを作成。
    person_list = []
    for object in 対象者マスタ.objects.filter(削除フラグ='0').exclude(対象者コード='0000000000').order_by('表示順序'):
        person_list.append((object.対象者コード, object.対象者名))

    # 日付項目は"datetimepicker"を利用してカレンダー入力を可能とする。
    # date = forms.CharField(max_length=8, label='日付')
    # date = forms.DateField(widget=AdminDateWidget(), label='日付')
    date = forms.CharField(widget=datetimepicker.DatePickerInput(
        format='%Y%m%d',
        options={
            'locale': 'ja',
            'dayViewHeaderFormat': 'YYYY年 MMMM',
        },
        attrs={'autofocus': 'autofocus'}
    ), label='日付')
    # 分類はプルダウンにする。
    # classify = forms.CharField(max_length=10, label='分類')
    classify = forms.ChoiceField(widget=forms.Select, choices=classify_list, label='分類')
    person = forms.ChoiceField(widget=forms.Select, choices=person_list, label='対象者')
    name = forms.CharField(max_length=100, label='項目名')
    money = forms.IntegerField(label='金額')
    is_tax = forms.BooleanField(widget=forms.CheckboxInput(), required=False, label='税')


class RegularForm(forms.Form):
    form_name = forms.CharField(label='フォーム名', required=False)
    date = forms.CharField(max_length=8, label='対象年月日', required=False, widget=forms.HiddenInput())
    classify_code = forms.CharField(max_length=10, label='支出分類コード', required=False, widget=forms.HiddenInput())
    person_code = forms.CharField(max_length=10, label='対象者コード', required=False, widget=forms.HiddenInput())
    money = forms.IntegerField(label='金額')


RegularFormSet = forms.formset_factory(RegularForm, extra=0)


class YMForm(forms.Form):
    YYYYMM = forms.CharField(max_length=6, label='年月')
