from django.urls import path
from . import views

urlpatterns = [
    # 日別支出一覧画面への遷移
    path('', views.view_list, name='view_list'),
    path('kakeibo/', views.view_list, name='view_list'),
]
