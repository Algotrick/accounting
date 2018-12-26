from rest_framework import serializers
from accounting.books.models import Organization, TaxRate, AbstractSale, AbstractSaleLine, Estimate, EstimateLine, Invoice, InvoiceLine, Bill, BillLine, ExpenseClaim, ExpenseClaimLine, Payment  
from django.contrib.auth.models import User
from accounting.people.models import Client, Employee
from accounting.reports.models import (BusinessSettings, FinancialSettings, PayRunSettings)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

class OrganizationSerializer(serializers.ModelSerializer):
    members = serializers.CharField(max_length=500)

    class Meta:
        model = Organization
        fields = (
            "display_name",
            "legal_name",
            "members",
            "owner",
        )

    def create(self, validated_data):
        print (validated_data, "**********")
        members = validated_data.pop('members')
        organization_obj = Organization.objects.create(**validated_data)
        organization_obj.members.clear()
        for each in members.split(','):
            organization_obj.members.add(User.objects.get(id=each))
        print (organization_obj.members.all())
        return organization_obj


class OrganizationListSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)

    class Meta:
        model = Organization
        fields = (
            "id",
            "display_name",
            "legal_name",
            "members",
            "owner",
        )


class TaxRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxRate
        fields = ['name', 'rate', 'organization', 'id']


class TaxRateListSerializer(serializers.ModelSerializer):
    organization = OrganizationListSerializer()

    class Meta:
        model = TaxRate
        fields = ['name', 'rate', 'organization', 'id']


class RestrictLineFormToOrganizationMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            if isinstance(instance, InvoiceLine):
                organization = instance.invoice.organization
            elif isinstance(instance, BillLine):
                organization = instance.bill.organization
            elif isinstance(instance, ExpenseClaimLine):
                organization = instance.expense_claim.organization
            else:
                raise NotImplementedError("The mixin has been applied to a "
                                          "form model that is not supported")
            self.restrict_to_organization(organization)

    def restrict_to_organization(self, organization):
        self.fields['tax_rate'].queryset = organization.tax_rates.all()


class EstimateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Estimate
        fields = (
            "number",
            "client",
            "date_issued",
            "date_dued",
        )


class EstimateLineSerializer(RestrictLineFormToOrganizationMixin,
                       serializers.ModelSerializer):
    class Meta:
        model = EstimateLine
        fields = (
            "label",
            "description",
            "unit_price_excl_tax",
            "quantity",
            "tax_rate",
        )

class ClientListSerializer(serializers.ModelSerializer):
    organization = OrganizationListSerializer()

    class Meta:
        model = Client
        fields = (
            "name",
            "address_line_1",
            "address_line_2",
            "city",
            "postal_code",
            "country",
            "organization"
        )

class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = (
            "name",
            "address_line_1",
            "address_line_2",
            "city",
            "postal_code",
            "country",
            "organization"
        )

class EmployeeListSerializer(serializers.ModelSerializer):
    organization = OrganizationListSerializer()

    class Meta:
        model = Employee
        fields = (
            "first_name",
            "last_name",
            "email",
            "payroll_tax_rate",
            "salary_follows_profits",
            "shares_percentage",
            "organization"
        )


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "first_name",
            "last_name",
            "email",
            "payroll_tax_rate",
            "salary_follows_profits",
            "shares_percentage",
            "organization"
        )


class BusinessSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessSettings
        fields = (
            "business_type", "organization"
        )


class FinancialSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinancialSettings
        fields = (
            "financial_year_end_day",
            "financial_year_end_month",

            "tax_id_number",
            "tax_id_display_name",
            "tax_period", "organization"
        )


class PayRunSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PayRunSettings
        fields = (
            "salaries_follow_profits",
            "payrun_period", "organization"
        )