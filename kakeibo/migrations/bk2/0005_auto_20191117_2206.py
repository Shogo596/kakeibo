# Generated by Django 2.2.6 on 2019-11-17 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0004_auto_20191117_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='支出明細',
            name='支出分類コード',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.支出分類マスタ'),
        ),
    ]
