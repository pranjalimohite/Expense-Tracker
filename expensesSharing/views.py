from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, GroupMember, GroupExpense, GroupExpenseShare
from .forms import GroupForm, GroupMemberForm, GroupExpenseForm
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

@login_required
def create_group(request):
    user_groups = Group.objects.filter(created_by=request.user)
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            # Add the creator as a member
            GroupMember.objects.create(group=group, user=request.user)
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm()
    return render(request, 'expensesSharing/create_group.html', {'form': form, 'user_groups': user_groups})

@login_required
def add_group_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.select_related('user').all()
    if request.method == 'POST':
        if 'remove_member_id' in request.POST:
            # Handle member removal
            member_id = request.POST.get('remove_member_id')
            member = get_object_or_404(GroupMember, id=member_id, group=group)
            # Prevent removing the group creator
            if member.user != group.created_by:
                member.delete()
            return redirect('add_group_member', group_id=group.id)
        else:
            form = GroupMemberForm(request.POST)
            if form.is_valid():
                member = form.save(commit=False)
                member.group = group
                # Prevent adding the same user twice
                if not GroupMember.objects.filter(group=group, user=member.user).exists():
                    member.save()
                return redirect('add_group_member', group_id=group.id)
    else:
        form = GroupMemberForm()
    return render(request, 'expensesSharing/add_group_member.html', {'form': form, 'group': group, 'members': members})

@login_required
def add_group_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.select_related('user').all()
    summary = None
    if request.method == 'POST':
        form = GroupExpenseForm(request.POST)
        shares = {str(m.user.id): request.POST.get(f'share_{m.user.id}') for m in members}
        if form.is_valid():
            amount = float(form.cleaned_data['amount'])
            total_share = 0
            share_values = {}
            for m in members:
                share_val = shares.get(str(m.user.id))
                try:
                    share = float(share_val)
                except (TypeError, ValueError):
                    share = 0
                total_share += share
                share_values[m.user] = share
            if abs(total_share - amount) > 0.01:
                form.add_error(None, 'Total split does not match expense amount!')
                return render(request, 'expensesSharing/add_group_expense.html', {'form': form, 'group': group, 'members': members, 'summary': None})
            # Save expense and shares
            expense = form.save(commit=False)
            expense.group = group
            expense.save()
            for user, share in share_values.items():
                GroupExpenseShare.objects.create(expense=expense, user=user, share=share)
            summary = [(user.username, share_values[user]) for user in share_values]
            return render(request, 'expensesSharing/add_group_expense.html', {'form': form, 'group': group, 'members': members, 'summary': summary, 'expense': expense})
    else:
        form = GroupExpenseForm()
    return render(request, 'expensesSharing/add_group_expense.html', {'form': form, 'group': group, 'members': members, 'summary': summary})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()
    expenses = group.expenses.all()
    return render(request, 'expensesSharing/group_detail.html', {'group': group, 'members': members, 'expenses': expenses})

@login_required
def group_expense_balances(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.select_related('user').all()
    expenses = group.expenses.all()
    # Calculate paid and owed for each user
    balances = {}
    for member in members:
        balances[member.user] = {'paid': 0, 'owed': 0}
    for expense in expenses:
        balances[expense.paid_by]['paid'] += float(expense.amount)
        for share in expense.shares.all():
            balances[share.user]['owed'] += float(share.share)
    # Prepare results
    results = []
    for user, data in balances.items():
        net = data['paid'] - data['owed']
        results.append({
            'username': user.username,
            'balance': round(net, 2),
            'status': 'gets' if net > 0 else ('owes' if net < 0 else 'settled')
        })
    return render(request, 'expensesSharing/group_expense_balances.html', {'group': group, 'results': results})

def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted successfully.')
        return redirect('home')  # Or wherever you want to redirect after deletion
    return redirect('group_detail', group_id=group_id)
