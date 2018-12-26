from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views import generic
import json
from rest_framework.views import APIView
from accounting.books.models import *
from accounting.books.forms import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from accounting.books.mixins import *
from accounting.books.utils import *
from accounting.people.models import Client, Employee
from accounting.people.forms import ClientForm, EmployeeForm
from accounting.reports.models import (
    BusinessSettings,
    FinancialSettings,
    PayRunSettings)
from accounting.reports.forms import (
    BusinessSettingsForm,
    FinancialSettingsForm,
    PayRunSettingsForm,
    TimePeriodForm)
from accounting.reports.wrappers import (
    TaxReport,
    ProfitAndLossReport,
    PayRunReport,
    InvoiceDetailsReport)
from dateutil.relativedelta import relativedelta

from accounting.books.utils import organization_manager
from accounting.libs.intervals import TimeInterval


# Create your views here.
def dashboard(request):
    return HttpResponse(json.dumps({'message': "hello"}))


class OrganizationSelectorView(APIView):

    def get(self, request):
        context = {}

        user = self.request.user
        orgas = organization_manager.get_user_organizations(user)
        cumulated_turnovers = (orgas
            .aggregate(sum=Sum('invoices__total_excl_tax'))["sum"]) or D('0')
        cumulated_debts = (orgas
            .aggregate(sum=Sum('bills__total_excl_tax'))["sum"]) or D('0')
        cumulated_profits = cumulated_turnovers - cumulated_debts

        context["organizations_count"] = orgas.count()
        context["organizations_cumulated_turnovers"] = cumulated_turnovers
        context["organizations_cumulated_profits"] = cumulated_profits
        context["organizations_cumulated_active_days"] = 0
        orgs = OrganizationListSerializer(orgas, many=True)
        context["organizations"] = orgs.data
        context["last_invoices"] = Invoice.objects.all()[:10]
        return Response(context)


class DashboardView(APIView):
    template_name = "books/dashboard.html"
    model = Organization
    context_object_name = "organization"

    def get_object(self):
        return organization_manager.get_selected_organization(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.get_object()
        ctx['invoices'] = (organization.invoices.all()
            .select_related(
                'client',
                'organization')
            .prefetch_related(
                'lines',
                'lines__tax_rate',
                'payments')
            .distinct())
        ctx['bills'] = (organization.bills.all()
            .select_related(
                'client',
                'organization')
            .prefetch_related(
                'lines',
                'lines__tax_rate',
                'payments')
            .distinct())
        return ctx

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrganizationListView(APIView):

    def get(self, request):
        # only current authenticated user organizations
        user_organizations = organization_manager.get_user_organizations(self.request.user)
        user_organizations_ser = OrganizationListSerializer(user_organizations, many=True)
        return Response(user_organizations_ser.data)


class OrganizationCreateView(APIView):
    # success_url = reverse_lazy("books:organization-list")

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationUpdateView(APIView):

    def post(self, request, pk):
        organization = Organization.objects.filter(id=pk).first()
        serializer = OrganizationSerializer(data=request.data, instance=organization, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            obj.owner = self.request.user
            obj.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationDetailView(APIView):

    def get(self, request, pk):
        ctx = {}
        organization = Organization.objects.filter(pk=pk).first()
        user_organizations_ser = OrganizationListSerializer(organization)
        ctx['organisation'] = user_organizations_ser.data 
        ctx['invoices'] = (organization.invoices.all()
            .select_related('client', 'organization')
            .prefetch_related('lines'))
        ctx['bills'] = (organization.bills.all()
            .select_related('client', 'organization')
            .prefetch_related('lines'))
        return Response(ctx)


class OrganizationSelectionView(APIView):

    def post(self, request, pk):
        organization = Organization.objects.filter(pk=pk).first()
        orga = OrganizationListSerializer(organization).data
        organization_manager.set_selected_organization(self.request, organization)
        return Response(orga, status=status.HTTP_201_CREATED)


class TaxRateListView(RestrictToSelectedOrganizationQuerySetMixin,
                      APIView):

    def get(self, request):
        # only current authenticated user organizations
        tax_rates = TaxRate.objects.filter()
        tax_rates = TaxRateListSerializer(tax_rates, many=True)
        return Response(tax_rates.data)


class TaxRateCreateView(AutoSetSelectedOrganizationMixin,
                        APIView):

    def post(self, request):
        print (request.data, "hjn")
        serializer = TaxRateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaxRateUpdateView(AutoSetSelectedOrganizationMixin,
                        APIView):

    def post(self, request, pk):
        print (request.data, "hjn")
        tax_rate = TaxRate.objects.filter(id=pk).first()
        serializer = TaxRateSerializer(data=request.data, instance=tax_rate, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaxRateDeleteView(APIView):

    def post(self, request, pk):
        print (request.data, "hjn")
        tax_rate = TaxRate.objects.filter(id=pk).first()
        if tax_rate:
            tax_rate.delete()
            return Response({'message': 'Deleted Successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'message': 'Deleted Successfully'}, status=status.HTTP_400_BAD_REQUEST)


class EstimateListView(RestrictToSelectedOrganizationQuerySetMixin,
                       SaleListQuerySetMixin,
                       APIView):

    def get(self, request):
        # only current authenticated user organizations
        estimates = Estimate.objects.filter()
        estimates = EstimateSerializer(estimates, many=True)
        return Response(estimates.data)


class EstimateCreateView(AutoSetSelectedOrganizationMixin,
                         AbstractSaleCreateUpdateMixin,
                         APIView):

    def post(self, request):
        initial = {}
        orga = organization_manager.get_selected_organization(self.request)
        print (orga, "********")
        initial['number'] = EstimateNumberGenerator().next_number(orga)
        return Response(initial, status=status.HTTP_201_CREATED)


class EstimateUpdateView(AutoSetSelectedOrganizationMixin,
                         AbstractSaleCreateUpdateMixin,
                         APIView):
    template_name = "books/estimate_create_or_update.html"
    model = Estimate
    form_class = EstimateForm
    formset_class = EstimateLineFormSet


class EstimateDeleteView(APIView):
    template_name = "_generics/delete_entity.html"
    model = Estimate


class EstimateDetailView(AbstractSaleDetailMixin,
                         APIView):
    template_name = "books/estimate_detail.html"
    model = Estimate
    context_object_name = "estimate"


class InvoiceListView(RestrictToSelectedOrganizationQuerySetMixin,
                      SaleListQuerySetMixin,
                      APIView):
    template_name = "books/invoice_list.html"
    model = Invoice
    context_object_name = "invoices"


class InvoiceCreateView(AutoSetSelectedOrganizationMixin,
                        AbstractSaleCreateUpdateMixin,
                        APIView):
    template_name = "books/invoice_create_or_update.html"
    model = Invoice
    form_class = InvoiceForm
    formset_class = InvoiceLineFormSet

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        orga = organization_manager.get_selected_organization(self.request)
        self.restrict_fields_choices_to_organization(form, orga)
        return form

    def get_initial(self):
        initial = super().get_initial()

        orga = organization_manager.get_selected_organization(self.request)
        initial['number'] = InvoiceNumberGenerator().next_number(orga)

        return initial


class InvoiceUpdateView(AutoSetSelectedOrganizationMixin,
                        AbstractSaleCreateUpdateMixin,
                        APIView):
    template_name = "books/invoice_create_or_update.html"
    model = Invoice
    form_class = InvoiceForm
    formset_class = InvoiceLineFormSet


class InvoiceDeleteView(APIView):
    template_name = "_generics/delete_entity.html"
    model = Invoice


class InvoiceDetailView(PaymentFormMixin,
                        AbstractSaleDetailMixin,
                        APIView):
    template_name = "books/invoice_detail.html"
    model = Invoice
    context_object_name = "invoice"
    payment_form_class = PaymentForm

    def get_success_url(self):
        return reverse('books:invoice-detail', args=[self.object.pk])


class BillListView(RestrictToSelectedOrganizationQuerySetMixin,
                   SaleListQuerySetMixin,
                   APIView):
    template_name = "books/bill_list.html"
    model = Bill
    context_object_name = "bills"


class BillCreateView(AutoSetSelectedOrganizationMixin,
                     AbstractSaleCreateUpdateMixin,
                     APIView):
    template_name = "books/bill_create_or_update.html"
    model = Bill
    form_class = BillForm
    formset_class = BillLineFormSet

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        orga = organization_manager.get_selected_organization(self.request)
        self.restrict_fields_choices_to_organization(form, orga)
        return form

    def get_initial(self):
        initial = super().get_initial()

        orga = organization_manager.get_selected_organization(self.request)
        initial['number'] = BillNumberGenerator().next_number(orga)

        return initial


class BillUpdateView(AutoSetSelectedOrganizationMixin,
                     AbstractSaleCreateUpdateMixin,
                     APIView):
    template_name = "books/bill_create_or_update.html"
    model = Bill
    form_class = BillForm
    formset_class = BillLineFormSet


class BillDeleteView(APIView):
    template_name = "_generics/delete_entity.html"
    model = Bill


class BillDetailView(PaymentFormMixin,
                     AbstractSaleDetailMixin,
                     APIView):
    template_name = "books/bill_detail.html"
    model = Bill
    context_object_name = "bill"
    payment_form_class = PaymentForm

    def get_success_url(self):
        return reverse('books:bill-detail', args=[self.object.pk])


class ExpenseClaimListView(RestrictToSelectedOrganizationQuerySetMixin,
                           SaleListQuerySetMixin,
                           APIView):
    template_name = "books/expense_claim_list.html"
    model = ExpenseClaim
    context_object_name = "expense_claims"


class ExpenseClaimCreateView(AutoSetSelectedOrganizationMixin,
                             AbstractSaleCreateUpdateMixin,
                             APIView):
    template_name = "books/expense_claim_create_or_update.html"
    model = ExpenseClaim
    form_class = ExpenseClaimForm
    formset_class = ExpenseClaimLineFormSet

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        orga = organization_manager.get_selected_organization(self.request)
        self.restrict_fields_choices_to_organization(form, orga)
        return form

    def get_initial(self):
        initial = super().get_initial()

        orga = organization_manager.get_selected_organization(self.request)
        initial['number'] = ExpenseClaimNumberGenerator().next_number(orga)

        return initial


class ExpenseClaimUpdateView(AutoSetSelectedOrganizationMixin,
                             AbstractSaleCreateUpdateMixin,
                             APIView):
    template_name = "books/expense_claim_create_or_update.html"
    model = ExpenseClaim
    form_class = ExpenseClaimForm
    formset_class = ExpenseClaimLineFormSet


class ExpenseClaimDeleteView(APIView):
    template_name = "_generics/delete_entity.html"
    model = ExpenseClaim


class ExpenseClaimDetailView(PaymentFormMixin,
                             AbstractSaleDetailMixin,
                             APIView):
    template_name = "books/expense_claim_detail.html"
    model = ExpenseClaim
    context_object_name = "expense_claim"
    payment_form_class = PaymentForm

    def get_success_url(self):
        return reverse('books:expense_claim-detail', args=[self.object.pk])


class ClientListView(RestrictToSelectedOrganizationQuerySetMixin,
                     APIView):

    def get(self, request):
        # only current authenticated user organizations
        clients = Client.objects.filter()
        clients = ClientListSerializer(clients, many=True)
        return Response(clients.data)


class ClientCreateView(AutoSetSelectedOrganizationMixin,
                       APIView):

    def post(self, request):
        serializer = ClientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientUpdateView(RestrictToSelectedOrganizationQuerySetMixin,
                       AutoSetSelectedOrganizationMixin,
                       APIView):

    def post(self, request, pk):
        client = Client.objects.filter(pk=pk).first()
        if client:
            serializer = ClientSerializer(data=request.data, instance=client, context={'request': request})
            if serializer.is_valid():
                obj = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'client not found with id'}, status=status.HTTP_400_BAD_REQUEST)


class ClientDetailView(RestrictToSelectedOrganizationQuerySetMixin,
                       APIView):

    def get(self, request, pk):
        # only current authenticated user organizations
        client = Client.objects.filter(pk=pk).first()
        if client:
            client = ClientListSerializer(client)
            return Response(client.data)
        else:
            return Response({'msg': 'employee not found with id'}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeListView(RestrictToSelectedOrganizationQuerySetMixin,
                       APIView):

    def get(self, request):
        # only current authenticated user organizations
        employees = Employee.objects.filter()
        employees = EmployeeListSerializer(employees, many=True)
        return Response(employees.data)


class EmployeeCreateView(AutoSetSelectedOrganizationMixin,
                         APIView):

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeUpdateView(RestrictToSelectedOrganizationQuerySetMixin,
                         AutoSetSelectedOrganizationMixin,
                         APIView):

    def post(self, request, pk):
        employee = Employee.objects.filter(pk=pk).first()
        if employee:
            serializer = EmployeeSerializer(data=request.data, instance=employee, context={'request': request})
            if serializer.is_valid():
                obj = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'employee not found with id'}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(RestrictToSelectedOrganizationQuerySetMixin,
                         APIView):

    def get(self, request, pk):
        # only current authenticated user organizations
        employees = Employee.objects.filter(pk=pk).first()
        if employees:
            employees = EmployeeListSerializer(employees)
            return Response(employees.data)
        else:
            return Response({'msg': 'employee not found with id'}, status=status.HTTP_400_BAD_REQUEST)


class TimePeriodFormMixin(object):

    period = None

    def get_initial(self):
        initial = super().get_initial()

        # currrent quarter
        now = timezone.now()
        start = date(
            year=now.year,
            month=(now.month - ((now.month - 1) % 3)),
            day=1
        )
        end = start + relativedelta(months=3)

        initial['date_from'] = start
        initial['date_to'] = end

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.GET:
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        form = ctx['form']
        if form.is_valid():
            start = form.cleaned_data['date_from']
            end = form.cleaned_data['date_to']
            ctx['form_title'] = form.get_filter_description()
        else:
            start = end = None
            ctx['form_title'] = "Time Interval"

        if self.period is None:
            self.period = TimeInterval(start=start, end=end)

        return ctx


class GenericSettingsMixin(object):

    def get_object(self):
        orga = organization_manager.get_selected_organization(self.request)
        try:
            settings = self.model.objects.get(organization=orga)
        except self.model.DoesNotExist:
            settings = self.model.objects.create(organization=orga)
        return settings


class BusinessSettingsUpdateView(GenericSettingsMixin,
                                 APIView):

    def get(self, request):
        orga = organization_manager.get_selected_organization(self.request)
        instance = BusinessSettings.objects.filter(organization=orga).first()
        if instance:
            validated_data = BusinessSettingsSerializer(data=request.data, instance=instance)
            return Response(validated_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'msg': 'no details found'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        orga = organization_manager.get_selected_organization(self.request)
        instance = BusinessSettings.objects.filter(organization=orga).first()
        if instance:
            validated_data = BusinessSettingsSerializer(data=request.data, instance=instance)
        else:
            validated_data = BusinessSettingsSerializer(data=request.data)
        if validated_data.is_valid():
            validated_data.save()
            return Response(validated_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                validated_data.errors, status=status.HTTP_400_BAD_REQUEST)


class FinancialSettingsUpdateView(GenericSettingsMixin,
                                  APIView):
    template_name = "reports/financial_settings_update.html"
    model = FinancialSettings
    form_class = FinancialSettingsForm

    def get(self, request):
        orga = organization_manager.get_selected_organization(self.request)
        instance = FinancialSettings.objects.filter(organization=orga).first()
        if instance:
            validated_data = FinancialSettingsSerializer(data=request.data, instance=instance)
            return Response(validated_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'msg': 'no details found'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        orga = organization_manager.get_selected_organization(self.request)
        instance = FinancialSettings.objects.filter(organization=orga).first()
        if instance:
            validated_data = FinancialSettingsSerializer(data=request.data, instance=instance)
        else:
            validated_data = FinancialSettingsSerializer(data=request.data)
        if validated_data.is_valid():
            validated_data.save()
            return Response(validated_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                validated_data.errors, status=status.HTTP_400_BAD_REQUEST)


class PayRunSettingsUpdateView(GenericSettingsMixin,
                               APIView):
    template_name = "reports/payrun_settings_update.html"
    model = PayRunSettings
    form_class = PayRunSettingsForm

    def get(self, request):
        orga = organization_manager.get_selected_organization(self.request)
        instance = PayRunSettings.objects.filter(organization=orga).first()
        if instance:
            validated_data = PayRunSettingsSerializer(instance=instance)
            return Response(validated_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'msg': 'no details found'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        orga = organization_manager.get_selected_organization(self.request)
        instance = PayRunSettings.objects.filter(organization=orga).first()
        if instance:
            validated_data = PayRunSettingsSerializer(data=request.data, instance=instance)
        else:
            validated_data = PayRunSettingsSerializer(data=request.data)
        if validated_data.is_valid():
            validated_data.save()
            return Response(validated_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                validated_data.errors, status=status.HTTP_400_BAD_REQUEST)


class TaxReportView(TimePeriodFormMixin,
                    generic.FormView):
    template_name = "reports/tax_report.html"
    form_class = TimePeriodForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orga = organization_manager.get_selected_organization(self.request)
        report = TaxReport(orga,
                           start=self.period.start,
                           end=self.period.end)
        report.generate()
        ctx['tax_summaries'] = report.tax_summaries.values()
        return ctx


class ProfitAndLossReportView(APIView):

    def get(self, request):
        ctx = {}
        orga = organization_manager.get_selected_organization(self.request)

        # currrent quarter
        now = timezone.now()
        start = date(
            year=now.year,
            month=(now.month - ((now.month - 1) % 3)),
            day=1
        )
        end = start + relativedelta(months=3)
        print (start, end, "******")
        report = ProfitAndLossReport(orga, start=start, end=end)
        report.generate()
        ctx['summaries'] = report.summaries
        ctx['total_summary'] = report.total_summary
        return Response(ctx, status=status.HTTP_201_CREATED)


class PayRunReportView(TimePeriodFormMixin,
                       generic.FormView):
    template_name = "reports/pay_run_report.html"
    form_class = TimePeriodForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orga = organization_manager.get_selected_organization(self.request)

        report = PayRunReport(orga,
                              start=self.period.start,
                              end=self.period.end)
        report.generate()
        ctx['summaries'] = report.summaries.values()
        ctx['total_payroll_taxes'] = report.total_payroll_taxes

        return ctx


class InvoiceDetailsView(TimePeriodFormMixin,
                         generic.FormView):
    template_name = "reports/invoice_details_report.html"
    form_class = TimePeriodForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orga = organization_manager.get_selected_organization(self.request)
        report = InvoiceDetailsReport(orga,
                                      start=self.period.start,
                                      end=self.period.end)
        report.generate()
        ctx['invoices'] = report.invoices
        ctx['tax_rates'] = report.tax_rates
        ctx['payrun_settings'] = orga.payrun_settings
        return ctx


class PaymentUpdateView(APIView):
    template_name = "books/payment_create_or_update.html"
    model = Payment
    form_class = PaymentForm

    def get_success_url(self):
        related_obj = self.object.content_object
        if isinstance(related_obj, Invoice):
            return reverse("books:invoice-detail", args=[related_obj.pk])
        elif isinstance(related_obj, Bill):
            return reverse("books:bill-detail", args=[related_obj.pk])

        logger.warning("Unsupported related object '{}' for "
                       "payment '{}'".format(self.object, related_obj))
        return reverse("books:dashboard")


class PaymentDeleteView(APIView):
    template_name = "_generics/delete_entity.html"
    model = Payment
