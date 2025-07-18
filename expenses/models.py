from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=100)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    CATEGORY_CHOICES = [
        ('Groceries', 'Groceries'),
        ('Rent', 'Rent'),
        ('Utilities', 'Utilities'),
        ('Transportation', 'Transportation'),
        ('Loan Payments', 'Loan Payments'),
        ('Entertainment', 'Entertainment'),
        ('Shopping', 'Shopping'),
        ('Travel', 'Travel'),
        ('Family & Personal', 'Family & Personal'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')

    def __str__(self):
        return f"{self.user.username} - {self.expense_type} - ₹{self.amount} on {self.date}"
