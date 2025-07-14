# reports/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.expense_summary_view, name='expense_summary'),
    path('expense/<int:expense_id>/delete/', views.delete_expense_view, name='delete_expense'),
    path('expense/<int:expense_id>/update/', views.update_expense_view, name='update_expense'),
    path('income-summary/', views.income_summary_view, name='income_summary'),
    path('download/', views.download_expense_report, name='download_expense_report'),
]

