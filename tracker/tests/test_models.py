import pytest
from tracker.models import Transaction

@pytest.mark.django_db
def test_queryset_get_income_method(transactions):
    qs= Transaction.objects.get_incomes()
    assert qs.count()> 0
    assert all([transaction.type=="income" for transaction in qs])

@pytest.mark.django_db
def test_queryset_get_expenses_method(transactions):
    qs= Transaction.objects.get_expenses()
    assert qs.count()> 0
    assert all([transaction.type=="expense" for transaction in qs])

@pytest.mark.django_db
def test_queryset_total_incomes_method(transactions):
    total_incomes= Transaction.objects.get_total_incomes()
    assert total_incomes == sum(t.amount for t in transactions if t.type=="income")

@pytest.mark.django_db
def test_queryset_get_total_expenses_method(transactions):
    total_expenses = Transaction.objects.get_total_expenses()
    assert total_expenses == sum(t.amount for t in transactions if t.type == 'expense')