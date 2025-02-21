import django_filters 
from tracker.models import Transaction , Category
from django import forms

class TransactionFilter(django_filters.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        choices=Transaction.TRANSACTION_TYPE_CHOICES,
        field_name='type',
        lookup_expr='iexact',
        empty_label='Any',
    )

    start_date= django_filters.DateFilter(
        field_name="date" ,
        widget= forms.DateInput(attrs={"type":"date"}),
        label = "date from" ,
        lookup_expr="gte" ,
    )

    end_date= django_filters.DateFilter(
        field_name="date" ,
        widget= forms.DateInput(attrs={"type":"date"}),
        label = "date to" ,
        lookup_expr="lte" ,
    )

    category= django_filters.ModelMultipleChoiceFilter(
        queryset= Category.objects.all(),
        widget= forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Transaction
        fields = ('transaction_type',"start_date","end_date" ,"category")