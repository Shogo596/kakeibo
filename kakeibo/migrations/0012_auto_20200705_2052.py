# Generated by Django 2.2.6 on 2020-07-05 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0011_auto_20200219_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='カード支出明細',
            name='作成年月日',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='収入支出明細',
            name='作成年月日',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='定例支出マスタ',
            name='作成年月日',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='支出基本',
            name='作成年月日',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
