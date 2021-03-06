# Generated by Django 2.2.6 on 2019-12-30 03:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='対象者マスタ',
            fields=[
                ('対象者コード', models.CharField(blank=True, max_length=10, primary_key=True, serialize=False)),
                ('対象者名', models.CharField(blank=True, max_length=100, null=True)),
                ('表示順序', models.IntegerField(blank=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, default='0', max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='支出分類マスタ',
            fields=[
                ('支出分類コード', models.CharField(blank=True, max_length=10, primary_key=True, serialize=False)),
                ('支出分類名', models.CharField(blank=True, max_length=100, null=True)),
                ('固定変動区分', models.CharField(blank=True, max_length=1, null=True)),
                ('表示順序', models.IntegerField(blank=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, default='0', max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='支出明細',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('対象年月日', models.CharField(blank=True, max_length=8, null=True)),
                ('項目名', models.CharField(blank=True, max_length=100, null=True)),
                ('金額', models.IntegerField(blank=True, null=True)),
                ('作成年月日', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('更新年月日', models.DateTimeField(auto_now=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, default='0', max_length=1, null=True)),
                ('対象者コード', models.ForeignKey(blank=True, default='0000000000', null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.対象者マスタ')),
                ('支出分類コード', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.支出分類マスタ')),
            ],
        ),
        migrations.CreateModel(
            name='支出基本',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('対象者コード', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('開始年月', models.CharField(blank=True, default='000000', max_length=6, null=True, unique=True)),
                ('終了年月', models.CharField(blank=True, default='999999', max_length=6, null=True)),
                ('金額', models.IntegerField(blank=True, null=True)),
                ('作成年月日', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('更新年月日', models.DateTimeField(auto_now=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, default='0', max_length=1, null=True)),
                ('支出分類コード', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.支出分類マスタ')),
            ],
        ),
    ]
