from django.shortcuts import render , get_object_or_404
from .models import Transaction
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_http_methods
from .filters import TransactionFilter
from .forms import TransactionForm
from django.core.paginator import Paginator
from django.conf import settings
from django_htmx.http import retarget
from tracker.charting import plot_income_expenses_bar_chart, plot_category_pie_chart
from tracker.resources import TransactionsResources
from django.http import HttpResponse
from tablib import Dataset


# Create your views here.
def index(request):
    return render(request, 'tracker/index.html')


@login_required
def transactions_list(request):
    transaction_filter= TransactionFilter(request.GET,queryset=Transaction.objects.filter(user=request.user).select_related('category'))
    paginator= Paginator(transaction_filter.qs , settings.PAGE_SIZE)
    transaction_page=paginator.page(1)

    total_income= transaction_filter.qs.get_total_incomes()
    total_expense= transaction_filter.qs.get_total_expenses()
    net_income= total_income - total_expense

    trans = Transaction.objects.filter(user=request.user)
    incomes=trans.get_total_incomes()
    expss=trans.get_total_expenses()
    nt= incomes - expss
    precentage= (nt / incomes) * 100 if incomes != 0 else 0

    context={"transactions":transaction_page,
            "filter":transaction_filter,
             "total_income":total_income ,
             "total_expense":total_expense ,
             "net_income": net_income ,
             'precentage':precentage }

    if request.htmx:
        return render(request, 'tracker/partials/transactions-container.html', context)
    
    return render(request, 'tracker/transactions-list.htm' , context)


@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {'message': "Transaction was added successfully!"}
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {'form': form}
            response = render(request, 'tracker/partials/create-transaction.html', context)
            return retarget(response, '#transaction-block')

    context = {'form': TransactionForm()}
    return render(request, 'tracker/partials/create-transaction.html', context)


@login_required
def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context = {'message': "Transaction was updated successfully!"}
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {
                'form': form,
                'transaction': transaction,
            }
            response = render(request, 'tracker/partials/update-transaction.html', context)
            return retarget(response, '#transaction-block')
        
    context = {
        'form': TransactionForm(instance=transaction),
        'transaction': transaction,
    }
    return render(request, 'tracker/partials/update-transaction.html', context)

@login_required
@require_http_methods (['DELETE'])
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    context = {'message': f"Transaction of {transaction.amount} on {transaction.date} was deleted successfully!"}
    return render(request, 'tracker/partials/transaction-success.html', context)



@login_required
def get_transactions(request):
    page = request.GET.get('page', 1)
    # time.sleep(1)  # ?page=2
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    context = {
        'transactions': paginator.page(page)
    }
    return render(
        request,
        'tracker/partials/transactions-container.html#transaction_list',
        context
    )



def transaction_charts(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs)

    category_income_pie = plot_category_pie_chart(
        transaction_filter.qs.filter(type='income')
    )
    category_expense_pie = plot_category_pie_chart(
        transaction_filter.qs.filter(type='expense')
    )

    context = {
        'filter': transaction_filter,
        'income_expense_barchart': income_expense_bar.to_html(),
        'category_income_pie': category_income_pie.to_html(),
        'category_expense_pie': category_expense_pie.to_html(),
    }
    if request.htmx:
        return render(request, 'tracker/partials/charts-container.html', context)
    return render(request, 'tracker/charts.html', context)



@login_required
def transaction_export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    data = TransactionsResources().export(transaction_filter.qs)
    response = HttpResponse(data.csv)
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    return response


@login_required
def transaction_import(request):
    if request.method == 'POST':
            file = request.FILES.get('file')
            resource = TransactionsResources()
            dataset = Dataset()
            dataset.load(file.read().decode(), format='csv')
            result = resource.import_data(dataset, user=request.user, dry_run=True)

            for row in result:
                for error in row.errors:
                    print(error)

            if not result.has_errors():
                resource.import_data(dataset, user=request.user, dry_run=False)
                context = {'message': f'{len(dataset)} transactions were uploaded successfully'}
            else:
                context = {'message': 'Sorry, an error occurred.'}
            return render(request, 'tracker/partials/transaction-success.html', context)
    return render(request, 'tracker/partials/transaction_import.html')