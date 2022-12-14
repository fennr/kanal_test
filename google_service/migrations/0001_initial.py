# Generated by Django 4.1.1 on 2022-09-28 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vbeln', models.IntegerField(unique=True, verbose_name='Order number')),
                ('dtime', models.DateTimeField(verbose_name='Delivery datetime')),
                ('price_usd', models.DecimalField(decimal_places=4, max_digits=15, verbose_name='Price $')),
                ('price_rub', models.DecimalField(decimal_places=4, max_digits=15, verbose_name='Price ₽')),
            ],
            options={
                'verbose_name': 'Order',
            },
        ),
    ]
