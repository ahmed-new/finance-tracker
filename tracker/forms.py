from django import forms
from tracker.models import Transaction, Category


class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Transaction
        fields = (
            'type',
            'amount',
            'date',
            'category',       
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def clean_amount(self):
        amount= self.cleaned_data['amount']
        if amount <= 0 :
            raise forms.ValidationError("The amount has to be a positive number ")
        return amount