# Generated by Django 2.1.3 on 2018-11-17 06:37

import accounting.libs.checks
import datetime
from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True, default=1)),
                ('total_incl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (inc. tax)')),
                ('total_excl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (excl. tax)')),
                ('date_issued', models.DateField(default=datetime.date.today)),
                ('date_dued', models.DateField(blank=True, help_text='The date when the total amount should have been collected', null=True, verbose_name='Due date')),
                ('date_paid', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-number',),
            },
            bases=(accounting.libs.checks.CheckingModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BillLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('unit_price_excl_tax', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True, default=1)),
                ('total_incl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (inc. tax)')),
                ('total_excl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (excl. tax)')),
                ('date_issued', models.DateField(default=datetime.date.today)),
                ('date_dued', models.DateField(blank=True, help_text='The date when the total amount should have been collected', null=True, verbose_name='Due date')),
                ('date_paid', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-number',),
            },
            bases=(accounting.libs.checks.CheckingModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EstimateLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('unit_price_excl_tax', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseClaim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True, default=1)),
                ('total_incl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (inc. tax)')),
                ('total_excl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (excl. tax)')),
                ('date_issued', models.DateField(default=datetime.date.today)),
                ('date_dued', models.DateField(blank=True, help_text='The date when the total amount should have been collected', null=True, verbose_name='Due date')),
                ('date_paid', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-number',),
            },
            bases=(accounting.libs.checks.CheckingModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ExpenseClaimLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('unit_price_excl_tax', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True, default=1)),
                ('total_incl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (inc. tax)')),
                ('total_excl_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='Total (excl. tax)')),
                ('date_issued', models.DateField(default=datetime.date.today)),
                ('date_dued', models.DateField(blank=True, help_text='The date when the total amount should have been collected', null=True, verbose_name='Due date')),
                ('date_paid', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-number',),
            },
            bases=(accounting.libs.checks.CheckingModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('unit_price_excl_tax', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='books.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(help_text='Name that you communicate', max_length=150)),
                ('legal_name', models.CharField(help_text='Official name to appear on your reports, sales invoices and bills', max_length=150)),
                ('members', models.ManyToManyField(blank=True, null=True, related_name='organizations', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_organizations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Amount')),
                ('detail', models.CharField(blank=True, max_length=255, null=True)),
                ('date_paid', models.DateField(default=datetime.date.today)),
                ('reference', models.CharField(blank=True, max_length=255, null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-date_paid',),
            },
        ),
        migrations.CreateModel(
            name='TaxRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('rate', models.DecimalField(decimal_places=5, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('1'))])),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tax_rates', to='books.Organization', verbose_name='Attached to Organization')),
            ],
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='tax_rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.TaxRate'),
        ),
    ]
