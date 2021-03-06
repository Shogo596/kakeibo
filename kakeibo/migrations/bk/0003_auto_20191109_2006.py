# Generated by Django 2.2.6 on 2019-11-09 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0002_支出明細'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='支出基本',
            name='支出基本id',
        ),
        migrations.RemoveField(
            model_name='支出明細',
            name='支出明細id',
        ),
        migrations.AddField(
            model_name='支出基本',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='支出明細',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='支出基本',
            name='支出分類コード',
            field=models.CharField(blank=True, default=1, max_length=10, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='支出基本',
            name='開始年月',
            field=models.CharField(blank=True, default='000000', max_length=6, unique=True),
        ),
    ]
