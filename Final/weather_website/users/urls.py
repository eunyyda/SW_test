from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 초기 화면 (기본 URL에 연결)
    path('login/', views.login, name='login'),  # 로그인
    path('signup/', views.signup, name='signup'),  # 회원가입
    path('weather/', views.weather, name='weather'),  # 날씨 화면
]