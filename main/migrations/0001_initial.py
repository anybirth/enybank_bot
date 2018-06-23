# Generated by Django 2.0.2 on 2018-06-23 19:39

from django.db import migrations, models
import django.db.models.deletion
import main.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bland',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='ブランド名')),
                ('data', models.CharField(max_length=50, unique=True, verbose_name='データ')),
                ('description', models.TextField(blank=True, verbose_name='備考')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'ブランド',
                'verbose_name_plural': 'ブランド',
                'db_table': 'blands',
            },
        ),
        migrations.CreateModel(
            name='ColorCategory',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='カラー分類名')),
                ('data', models.CharField(max_length=50, unique=True, verbose_name='データ')),
                ('description', models.TextField(blank=True, verbose_name='備考')),
                ('code', models.CharField(max_length=50, verbose_name='カラーコード')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'カラー分類',
                'verbose_name_plural': 'カラー分類',
                'db_table': 'color_categories',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('color', models.CharField(max_length=50, verbose_name='カラー')),
                ('name', models.CharField(max_length=50, verbose_name='商品名')),
                ('data', models.CharField(max_length=50, unique=True, verbose_name='データ')),
                ('description', models.TextField(blank=True, verbose_name='備考')),
                ('capacity', models.IntegerField(verbose_name='容量')),
                ('is_tsa', models.BooleanField(verbose_name='TSAロック対応')),
                ('fee_intercept', models.IntegerField(verbose_name='料金切片')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('bland', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Bland', verbose_name='ブランド')),
                ('color_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='color_category_set', to='main.ColorCategory', verbose_name='カラー分類')),
            ],
            options={
                'verbose_name': 'アイテム',
                'verbose_name_plural': 'アイテム',
                'db_table': 'items',
            },
        ),
        migrations.CreateModel(
            name='ItemFeeCoef',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('fee_coef', models.IntegerField(verbose_name='料金係数')),
                ('starting_point', models.SmallIntegerField(verbose_name='起点日数')),
                ('end_point', models.SmallIntegerField(blank=True, null=True, verbose_name='終点日数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_fee_coef_set', to='main.Item', verbose_name='アイテム')),
            ],
            options={
                'verbose_name': 'アイテム料金係数',
                'verbose_name_plural': 'アイテム料金係数',
                'db_table': 'item_fee_coefs',
            },
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to=main.models.ItemImage._get_image_path, verbose_name='画像')),
                ('order', models.SmallIntegerField(verbose_name='表示順')),
                ('description', models.TextField(blank=True, verbose_name='備考')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_image_set', to='main.Item', verbose_name='アイテム')),
            ],
            options={
                'verbose_name': 'アイテム画像',
                'verbose_name_plural': 'アイテム画像',
                'db_table': 'item_images',
            },
        ),
        migrations.CreateModel(
            name='LINEUser',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('line_id', models.CharField(max_length=255, verbose_name='LINE ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='氏名')),
                ('zip_code', models.CharField(blank=True, max_length=50, verbose_name='郵便番号')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='住所')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'LINEユーザー',
                'verbose_name_plural': 'LINEユーザー',
                'db_table': 'line_users',
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='開始日')),
                ('return_date', models.DateField(blank=True, null=True, verbose_name='返却日')),
                ('zip_code', models.CharField(blank=True, max_length=50, verbose_name='郵便番号')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='住所')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='氏名')),
                ('item_fee', models.IntegerField(blank=True, null=True, verbose_name='小計価格')),
                ('postage', models.IntegerField(blank=True, null=True, verbose_name='送料')),
                ('total_fee', models.IntegerField(blank=True, null=True, verbose_name='合計価格')),
                ('status', models.SmallIntegerField(default=1, verbose_name='ステータス')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='main.Item', verbose_name='アイテム')),
                ('line_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.LINEUser', verbose_name='LINEユーザー')),
            ],
            options={
                'verbose_name': '予約',
                'verbose_name_plural': '予約',
                'db_table': 'reservations',
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='サイズ名')),
                ('data', models.CharField(max_length=50, unique=True, verbose_name='データ')),
                ('description', models.TextField(blank=True, verbose_name='備考')),
                ('min_days', models.SmallIntegerField(verbose_name='最小日数')),
                ('max_days', models.SmallIntegerField(blank=True, null=True, verbose_name='最大日数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'サイズ',
                'verbose_name_plural': 'サイズ',
                'db_table': 'sizes',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='タイプ名')),
                ('data', models.CharField(max_length=50, unique=True, verbose_name='データ')),
                ('description', models.TextField(blank=True, verbose_name='備考')),
                ('image', models.ImageField(upload_to=main.models.Type._get_image_path, verbose_name='画像')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'タイプ',
                'verbose_name_plural': 'タイプ',
                'db_table': 'types',
            },
        ),
        migrations.AddField(
            model_name='reservation',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='main.Size', verbose_name='サイズ'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='main.Type', verbose_name='タイプ'),
        ),
        migrations.AddField(
            model_name='item',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Size', verbose_name='サイズ'),
        ),
        migrations.AddField(
            model_name='item',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Type', verbose_name='タイプ'),
        ),
    ]