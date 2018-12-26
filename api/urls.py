from django.conf.urls import include, url

from .views import *


app_name = 'books'

urlpatterns = [
    url(r'^dashboard/$', dashboard, name="dashboard"),

    # Organizations
    url(r'^organization/$', OrganizationListView.as_view(), name="organization-list"),
    url(r'^organization/selector/$', OrganizationSelectorView.as_view(), name="organization-selector"),
    url(r'^organization/create/$', OrganizationCreateView.as_view(), name="organization-create"),
    url(r'^organization/(?P<pk>\d+)/edit/$', OrganizationUpdateView.as_view(), name="organization-edit"),
    url(r'^organization/(?P<pk>\d+)/detail/$', OrganizationDetailView.as_view(), name="organization-detail"),
    url(r'^organization/(?P<pk>\d+)/select/$', OrganizationSelectionView.as_view(), name="organization-select"),

    # Tax Rates
    url(r'^tax_rates/$', TaxRateListView.as_view(), name="tax_rate-list"),
    url(r'^tax_rates/create/$', TaxRateCreateView.as_view(), name="tax_rate-create"),
    url(r'^tax_rates/(?P<pk>\d+)/edit/$', TaxRateUpdateView.as_view(), name="tax_rate-edit"),
    url(r'^tax_rates/(?P<pk>\d+)/delete/$', TaxRateDeleteView.as_view(), name="tax_rate-delete"),

    # Clients
    url(r'^client/$', ClientListView.as_view(), name="client-list"),
    url(r'^client/create/$', ClientCreateView.as_view(), name="client-create"),
    url(r'^client/(?P<pk>\d+)/edit/$', ClientUpdateView.as_view(), name="client-edit"),
    url(r'^client/(?P<pk>\d+)/detail/$', ClientDetailView.as_view(), name="client-detail"),

    # Employees
    url(r'^employee/$', EmployeeListView.as_view(), name="employee-list"),
    url(r'^employee/create/$', EmployeeCreateView.as_view(), name="employee-create"),
    url(r'^employee/(?P<pk>\d+)/edit/$', EmployeeUpdateView.as_view(), name="employee-edit"),
    url(r'^employee/(?P<pk>\d+)/detail/$', EmployeeDetailView.as_view(), name="employee-detail"),

    # Estimates
    url(r'^estimate/$', EstimateListView.as_view(), name="estimate-list"),
    url(r'^estimate/create/$', EstimateCreateView.as_view(), name="estimate-create"),
    url(r'^estimate/(?P<pk>\d+)/edit/$', EstimateUpdateView.as_view(), name="estimate-edit"),
    url(r'^estimate/(?P<pk>\d+)/delete/$', EstimateDeleteView.as_view(), name="estimate-delete"),
    url(r'^estimate/(?P<pk>\d+)/detail/$', EstimateDetailView.as_view(), name="estimate-detail"),

    # Bills
    url(r'^bill/$', BillListView.as_view(), name="bill-list"),
    url(r'^bill/create/$', BillCreateView.as_view(), name="bill-create"),
    url(r'^bill/(?P<pk>\d+)/edit/$', BillUpdateView.as_view(), name="bill-edit"),
    url(r'^bill/(?P<pk>\d+)/delete/$', BillDeleteView.as_view(), name="bill-delete"),
    url(r'^bill/(?P<pk>\d+)/detail/$', BillDetailView.as_view(), name="bill-detail"),

    # ExpenseClaims
    url(r'^expense-claim/$', ExpenseClaimListView.as_view(), name="expense_claim-list"),
    url(r'^expense-claim/create/$', ExpenseClaimCreateView.as_view(), name="expense_claim-create"),
    url(r'^expense-claim/(?P<pk>\d+)/edit/$', ExpenseClaimUpdateView.as_view(), name="expense_claim-edit"),
    url(r'^expense-claim/(?P<pk>\d+)/delete/$', ExpenseClaimDeleteView.as_view(), name="expense_claim-delete"),
    url(r'^expense-claim/(?P<pk>\d+)/detail/$', ExpenseClaimDetailView.as_view(), name="expense_claim-detail"),

    # Payments
    url(r'^payment/(?P<pk>\d+)/edit/$', PaymentUpdateView.as_view(), name="payment-edit"),
    url(r'^payment/(?P<pk>\d+)/delete/$', PaymentDeleteView.as_view(), name="payment-delete"),

    # Reports
    url(r'^report/tax/$', TaxReportView.as_view(), name="tax-report"),
    url(r'^report/profitloss/$', ProfitAndLossReportView.as_view(), name="profit-and-loss-report"),
    url(r'^report/payrun/$', PayRunReportView.as_view(), name="pay-run-report"),
    url(r'^report/invoicedetails/$', InvoiceDetailsView.as_view(), name="invoice-details-report"),

    # Settings
    url(r'^settings/business/$', BusinessSettingsUpdateView.as_view(), name="settings-business"),
    url(r'^settings/financial/$', FinancialSettingsUpdateView.as_view(), name="settings-financial"),
    url(r'^settings/payrun/$', PayRunSettingsUpdateView.as_view(), name="settings-payrun"),

]
