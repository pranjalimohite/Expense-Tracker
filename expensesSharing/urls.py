from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_group, name='create_group'),
    path('<int:group_id>/add_member/', views.add_group_member, name='add_group_member'),
    path('<int:group_id>/add_expense/', views.add_group_expense, name='add_group_expense'),
    path('<int:group_id>/balances/', views.group_expense_balances, name='group_expense_balances'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),
] 