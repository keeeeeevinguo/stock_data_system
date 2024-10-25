"""
URL configuration for financial project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from stockapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('fetch/<str:symbol>/', views.fetch_financial_data, name='fetch_financial_data'),
    path('fetch_with_retry/<str:symbol>/', views.fetch_financial_data_with_retry, name='fetch_financial_data_with_retry'),
    path('backtest/<str:symbol>/<int:initial_investment>/', views.backtest_strategy, name='backtest_strategy'),
    path('predict/<str:symbol>/', views.predict_stock_prices, name='predict_stock_prices'),
    path('report/<str:symbol>/', views.generate_report, name='generate_report'),
]
