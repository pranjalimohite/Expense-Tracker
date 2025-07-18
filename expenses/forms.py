from django import forms
from .models import Budget
from .models import Expense

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter budget amount',
                'class': 'form-control'
            }),
        }
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'expense_type', 'date']  # Do not include 'category' so it is set automatically
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }