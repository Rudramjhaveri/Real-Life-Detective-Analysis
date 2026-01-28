from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('case/<int:id>/', views.case_detail_view, name='case_detail'),
    path('case/<int:id>/solve/', views.solve_view, name='solve'),
    path('case/<int:case_id>/execute_query/', views.execute_query_view, name='execute_query'),
    path('case/<int:case_id>/execute_python/', views.execute_python_view, name='execute_python'),
    path('result/', views.result_view, name='result'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
