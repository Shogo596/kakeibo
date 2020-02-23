# Generated by Django 2.2.6 on 2020-02-19 04:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0008_auto_20200209_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='収入支出分類マスタ',
            fields=[
                ('収入支出分類コード', models.CharField(blank=True, max_length=10, primary_key=True, serialize=False)),
                ('収入支出分類名', models.CharField(blank=True, max_length=100, null=True)),
                ('収入支出区分', models.CharField(blank=True, max_length=1, null=True)),
                ('固定変動区分', models.CharField(blank=True, max_length=1, null=True)),
                ('対象者区別有無', models.CharField(blank=True, max_length=1, null=True)),
                ('表示順序', models.IntegerField(blank=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, default='0', max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='収入支出明細',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('対象年月日', models.CharField(blank=True, max_length=8, null=True)),
                ('項目名', models.CharField(blank=True, max_length=100, null=True)),
                ('金額', models.IntegerField(blank=True, null=True)),
                ('作成年月日', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('更新年月日', models.DateTimeField(auto_now=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, default='0', max_length=1, null=True)),
                ('収入支出分類コード', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.収入支出分類マスタ')),
                ('対象者コード', models.ForeignKey(blank=True, default='0000000000', null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.対象者マスタ')),
            ],
        ),
        migrations.RemoveField(
            model_name='支出明細',
            name='対象者コード',
        ),
        migrations.RemoveField(
            model_name='支出明細',
            name='支出分類コード',
        ),
        migrations.AlterField(
            model_name='カード支出明細',
            name='支出分類コード',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.収入支出分類マスタ'),
        ),
        migrations.AlterField(
            model_name='定例支出マスタ',
            name='支出分類コード',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.収入支出分類マスタ'),
        ),
        migrations.AlterField(
            model_name='支出基本',
            name='支出分類コード',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kakeibo.収入支出分類マスタ'),
        ),
        migrations.DeleteModel(
            name='支出分類マスタ',
        ),
        migrations.DeleteModel(
            name='支出明細',
        ),
    ]
