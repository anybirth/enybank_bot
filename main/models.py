import os
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

def get_image_path(instance, filename):
    name = str(uuid.uuid4()).replace('-', '')
    extension = os.path.splitext(filename)[-1]
    return name + extension



class UUIDModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class Size(UUIDModel):
    name = models.CharField(_('サイズ名'), max_length=50)
    description = models.TextField(_('備考'), blank=True)
    min_days = models.SmallIntegerField(_('最小日数'))
    max_days = models.SmallIntegerField(_('最大日数'), blank=True, null=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'sizes'
        ordering = ['min_days']
        verbose_name = _('サイズ')
        verbose_name_plural = _('サイズ')

    def __str__(self):
        return '%s' % self.name

class Type(UUIDModel):

    def _get_image_path(self, filename):
        prefix = 'img/type/'
        path = get_image_path(self, filename)
        return prefix + path

    name = models.CharField(_('タイプ名'), max_length=50)
    description = models.TextField(_('備考'), blank=True)
    image = models.ImageField(upload_to=_get_image_path, verbose_name=_('画像'))
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'types'
        ordering = ['name']
        verbose_name = _('タイプ')
        verbose_name_plural = _('タイプ')

    def __str__(self):
        return '%s' % self.name

class ColorCategory(UUIDModel):
    name = models.CharField(_('カラー分類名'), max_length=50)
    description = models.TextField(_('備考'), blank=True)
    code = models.CharField(_('カラーコード'), max_length=50)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'color_categories'
        ordering = ['name']
        verbose_name = _('カラー分類')
        verbose_name_plural = _('カラー分類')

    def __str__(self):
        return '%s' % self.name

class Bland(UUIDModel):
    name = models.CharField(_('ブランド名'), max_length=50)
    description = models.TextField(_('備考'), blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'blands'
        ordering = ['name']
        verbose_name = _('ブランド')
        verbose_name_plural = _('ブランド')

    def __str__(self):
        return '%s' % self.name

class Item(UUIDModel):
    bland = models.ForeignKey('Bland', on_delete=models.PROTECT, verbose_name=_('ブランド'))
    size = models.ForeignKey('Size', on_delete=models.PROTECT, verbose_name=_('サイズ'))
    type = models.ForeignKey('Type', on_delete=models.PROTECT, verbose_name=_('タイプ'))
    color_category = models.ForeignKey('ColorCategory', on_delete=models.PROTECT, verbose_name=_('カラー分類'), related_name='color_category_set')
    color = models.CharField(_('カラー'), max_length=50)
    name = models.CharField(_('商品名'), max_length=50)
    description = models.TextField(_('備考'), blank=True)
    capacity = models.IntegerField(_('容量'))
    is_tsa = models.BooleanField(_('TSAロック対応'), default=True)
    fee_intercept = models.IntegerField(_('料金切片'))
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'items'
        ordering = ['bland__name', 'capacity', 'name']
        verbose_name = _('アイテム')
        verbose_name_plural = _('アイテム')

    def __str__(self):
        return '%s' % self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ItemFeeCoef.objects.filter(item=self).delete()
        self.item_fee_coef_set.get_or_create(
            fee_coef=round((self.fee_intercept / .6) * .2, -1),
            starting_point=0,
            end_point=3
        )
        self.item_fee_coef_set.get_or_create(
            fee_coef=round((self.fee_intercept / .6) * .15, -1),
            starting_point=3,
            end_point=5
        )
        self.item_fee_coef_set.get_or_create(
            fee_coef=round((self.fee_intercept / .6) * .13, -1),
            starting_point=5
        )

class ItemFeeCoef(UUIDModel):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, verbose_name=_('アイテム'), related_name='item_fee_coef_set')
    fee_coef = models.IntegerField(_('料金係数'))
    starting_point = models.SmallIntegerField(_('起点日数'))
    end_point = models.SmallIntegerField(_('終点日数'), blank=True, null=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'item_fee_coefs'
        ordering = ['item__bland__name', 'item__capacity', 'item__name', 'starting_point']
        verbose_name = _('アイテム料金係数')
        verbose_name_plural = _('アイテム料金係数')

    def __str__(self):
        return '%s' % self.item.name

class ItemImage(UUIDModel):

    def _get_image_path(self, filename):
        prefix = 'img/item/'
        path = get_image_path(self, filename)
        return prefix + path

    item = models.ForeignKey('Item', on_delete=models.CASCADE, verbose_name=_('アイテム'), related_name='item_image_set')
    image = models.ImageField(upload_to=_get_image_path, verbose_name=_('画像'))
    order = models.SmallIntegerField(_('表示順'))
    description = models.TextField(_('備考'), blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'item_images'
        ordering = ['item__bland__name', 'item__capacity', 'item__name', 'order']
        verbose_name = _('アイテム画像')
        verbose_name_plural = _('アイテム画像')

    def __str__(self):
        return '%s' % self.item.name

class LINEUser(UUIDModel):
    line_id = models.CharField(_('LINE ID'), max_length=255)
    name = models.CharField(_('氏名'), max_length=50, blank=True, null=True)
    zip_code = models.CharField(_('郵便番号'), max_length=50, blank=True)
    address = models.CharField(_('住所'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'line_users'
        ordering = ['-created_at']
        verbose_name = _('LINEユーザー')
        verbose_name_plural = _('LINEユーザー')

    def __str__(self):
        return '%s' % self.name

class Reservation(UUIDModel):
    line_user = models.ForeignKey('LINEUser', on_delete=models.CASCADE, verbose_name=_('LINEユーザー'))
    item = models.ForeignKey('Item', on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('アイテム'))
    size = models.ForeignKey('Size', on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('サイズ'))
    type = models.ForeignKey('Type', on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('タイプ'))
    start_date = models.DateField(_('開始日'), blank=True, null=True)
    return_date = models.DateField(_('返却日'), blank=True, null=True)
    zip_code = models.CharField(_('郵便番号'), max_length=50, blank=True)
    address = models.CharField(_('住所'), max_length=255, blank=True)
    name = models.CharField(_('氏名'), max_length=50, blank=True, null=True)
    item_fee = models.IntegerField(_('小計価格'), blank=True, null=True)
    postage = models.IntegerField(_('送料'), blank=True, null=True)
    total_fee = models.IntegerField(_('合計価格'), blank=True, null=True)
    status = models.SmallIntegerField(_('ステータス'), default=1)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        db_table = 'reservations'
        ordering = ['-created_at']
        verbose_name = _('予約')
        verbose_name_plural = _('予約')

    def __str__(self):
        return '%s' % self.line_user
