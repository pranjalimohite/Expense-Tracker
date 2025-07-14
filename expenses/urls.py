from django.urls import path
from . import views

urlpatterns = [
    
    path('add-budget/', views.add_budget_view, name='add_budget'),
    path('add-expense/', views.add_expense_view, name='add_expense'),
    
    
    
  


]
