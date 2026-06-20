from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('assessment/', views.assessment, name='assessment'),
    path('results/<int:response_id>/', views.results, name='results'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
    path('dashboard/drilldown/', views.dashboard_drilldown, name='dashboard_drilldown'),
    path('risk-analysis/', views.risk_analysis, name='risk_analysis'),
    path('recommendations/', views.recommendations, name='recommendations'),
]
