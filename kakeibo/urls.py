from django.urls import path
from . import views

# mysite.urlsとの調整を行う。すべてのURLにkakeiboがあるのはおかしいかも。
app_name = 'Kakeibo'
urlpatterns = [
    # 日別支出一覧画面への遷移
    path('', views.view_list, name='top'),
    path('kakeibo/', views.view_list, name='kakeibo_top'),
    path('kakeibo/view_list/', views.view_list, name='view_list'),

    # 例月支出登録画面への遷移
    path('kakeibo/regist_regular_expense/', views.regist_regular_expense, name='regist_regular_expense'),

    # クレジットカードデータ登録画面への遷移
    path('kakeibo/credit_card_regist/', views.credit_card_regist, name='credit_card_regist'),
]
