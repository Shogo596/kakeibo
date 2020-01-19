from django.urls import path
from . import views

urlpatterns = [
    # 日別支出一覧画面への遷移
    path('', views.view_list, name='view_list'),
    path('kakeibo/', views.view_list, name='view_list'),
    path('kakeibo/view_list/', views.view_list, name='view_list'),

    # 例月支出登録画面への遷移
    path('kakeibo/regist_regular_expense/', views.regist_regular_expense, name='regist_regular_expense'),
]
