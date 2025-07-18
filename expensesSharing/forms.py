from django import forms
from .models import Group, GroupMember, GroupExpense

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ['user']

class GroupExpenseForm(forms.ModelForm):
    class Meta:
        model = GroupExpense
        fields = ['description', 'amount', 'paid_by'] 