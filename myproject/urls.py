"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from users import views as user_views
from expenses import views as expense_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('login/', user_views.login_view, name='login'),
    path('users/', include('users.urls')),
    path('expenses/', include('expenses.urls')), 
    path('reports/', include('reports.urls')),
    path('dashboard/', expense_views.dashboard_view, name='dashboard'),
    path('add-budget/', expense_views.add_budget_view, name='add_budget'),
    path('add-expense/', expense_views.add_expense_view, name='add_expense'),
    path('groups/', include('expensesSharing.urls')),
]

