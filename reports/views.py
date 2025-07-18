from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.urls import reverse
from expenses.forms import BudgetForm, ExpenseForm
from expenses.models import Expense, Budget
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils.timezone import now
from calendar import monthrange

import json
import csv
from django.http import HttpResponse
from expenses.models import Expense
from collections import defaultdict


@login_required
def expense_summary_view(request):
    # Fetch expenses
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    # Group expenses by category
    categorized_expenses = defaultdict(list)
    for expense in expenses:
        categorized_expenses[expense.category].append(expense)

    # Total expense
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Total budget
    total_budget = Budget.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Savings and balance
    savings = total_budget - total_expense
    balance = savings  # or update if you track balance separately

    # Chart data: Pie (by category/type)
    expense_by_type = expenses.values('expense_type').annotate(total=Sum('amount'))

    # Chart data: Bar (monthly totals)
    monthly_expenses = expenses.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')

    # Current & Last Month Setup
    today = now().date()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)

    current_month_expenses = expenses.filter(date__gte=first_day_this_month)
    last_month_expenses = expenses.filter(date__gte=first_day_last_month, date__lte=last_day_last_month)

    current_month_total = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    last_month_total = last_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Comparison
    comparison = current_month_total - last_month_total
    percentage_change = (
        (comparison / last_month_total * 100) if last_month_total != 0 else 100
    )
    days_in_current_month = monthrange(today.year, today.month)[1]
    daily_average = current_month_total / days_in_current_month
    monthly_average = total_expense / len(monthly_expenses) if monthly_expenses else 0

    # Extremes
    biggest_category = max(expense_by_type, key=lambda x: x['total'], default={'expense_type': 'N/A', 'total': 0})
    smallest_category = min(expense_by_type, key=lambda x: x['total'], default={'expense_type': 'N/A', 'total': 0})
    biggest_expense = expenses.order_by('-amount').first()
    smallest_expense = expenses.order_by('amount').first()

   
    expense_percentage = (total_expense / total_budget) * 100 if total_budget > 0 else 0

    if expense_percentage < 50:
        progress_color = '#4CAF50'  # green
    elif expense_percentage < 75:
        progress_color = '#FFC107'  # yellow
    else:
        progress_color = '#F44336'  # red


    context = {
        'expenses': expenses,
        'categorized_expenses': categorized_expenses,
        'total_expense': total_expense,
        'total_budget': total_budget,
        'savings': savings,
        'balance': balance,
    # Chart Data
        'expense_type_labels': json.dumps([e['expense_type'] for e in expense_by_type]),
        'expense_type_data': json.dumps([float(e['total']) for e in expense_by_type]),

        'monthly_labels': json.dumps([e['month'].strftime('%b %Y') for e in monthly_expenses]),
        'monthly_data': json.dumps([float(e['total']) for e in monthly_expenses]),

        # Summary Metrics
        'current_month_total': current_month_total,
        'last_month_total': last_month_total,
        'comparison': comparison,
        'percentage_change': round(percentage_change, 2),
        'daily_average': round(daily_average, 2),
        'monthly_average': round(monthly_average, 2),
        'biggest_category': biggest_category,
        'smallest_category': smallest_category,
        'biggest_expense': biggest_expense,
        'smallest_expense': smallest_expense,
        'expense_percentage': round(expense_percentage, 2),
        'progress_color': progress_color,

    }

    return render(request, 'reports/expense_summary.html', context)




@login_required
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_summary')
    return render(request, 'reports/confirm_delete_expense.html', {'expense': expense})

@login_required
def update_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_summary')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/add_expense.html', {'form': form, 'update': True})

@login_required
def income_summary_view(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    total_income = budgets.aggregate(total=Sum('amount'))['total'] or 0

    # Monthly budget chart data
    monthly_budgets = budgets.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('amount')).order_by('month')
    monthly_budget_labels = json.dumps([e['month'].strftime('%b %Y') for e in monthly_budgets])
    monthly_budget_data = json.dumps([float(e['total']) for e in monthly_budgets])

    # Find highest and lowest budget months
    highest_month = None
    lowest_month = None
    if monthly_budgets:
        highest = max(monthly_budgets, key=lambda x: x['total'])
        lowest = min(monthly_budgets, key=lambda x: x['total'])
        highest_month = {'label': highest['month'].strftime('%b %Y'), 'total': highest['total']}
        lowest_month = {'label': lowest['month'].strftime('%b %Y'), 'total': lowest['total']}

    return render(request, 'reports/income_summary.html', {
        'budgets': budgets,
        'total_income': total_income,
        'monthly_budget_labels': monthly_budget_labels,
        'monthly_budget_data': monthly_budget_data,
        'highest_month': highest_month,
        'lowest_month': lowest_month,
    })
def download_expense_report(request):
    # Create the HttpResponse object with CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Amount'])

    # Query all expenses (customize as needed)
    expenses = Expense.objects.all()
    for expense in expenses:
        writer.writerow([expense.date, expense.expense_type, expense.amount])

    return response
# Create your views here.
