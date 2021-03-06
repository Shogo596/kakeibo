# Generated by Django 2.2.6 on 2019-11-09 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShisyutuKihon',
            fields=[
                ('支出基本id', models.IntegerField(db_column='支出基本ID', primary_key=True, serialize=False)),
                ('支出分類コード', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('対象者コード', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('開始年月', models.CharField(blank=True, max_length=6, null=True, unique=True)),
                ('終了年月', models.CharField(blank=True, max_length=6, null=True)),
                ('金額', models.IntegerField(blank=True, null=True)),
                ('作成年月日', models.DateTimeField(blank=True, null=True)),
                ('更新年月日', models.DateTimeField(blank=True, null=True)),
                ('削除フラグ', models.CharField(blank=True, max_length=1, null=True)),
            ],
        ),
    ]
