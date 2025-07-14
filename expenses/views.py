
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BudgetForm
from .models import Budget
from django.db.models import Sum
from .forms import ExpenseForm
from .models import Expense
from django.urls import reverse

@login_required
def dashboard_view(request):
    budgets = Budget.objects.filter(user=request.user)
    total_budget = budgets.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'users/dashboard.html', {
        'user': request.user,
        'budgets': budgets,
        'total_budget': total_budget,
    })

@login_required
def add_budget_view(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('dashboard')
    else:
        form = BudgetForm()
    return render(request, 'expenses/add_budget.html', {'form': form})
@login_required
def add_expense_view(request):
       if request.method == 'POST':
           form = ExpenseForm(request.POST)
           if form.is_valid():
               expense = form.save(commit=False)
               expense.user = request.user
               expense.save()
               return redirect('dashboard')
       else:
           form = ExpenseForm()
       return render(request, 'expenses/add_expense.html', {'form': form})
