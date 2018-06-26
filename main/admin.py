from django.contrib import admin
from django import forms
from . import models

# Register your models here.

class ItemInline(admin.TabularInline):
    model = models.Item
    can_delete = True
    show_change_link = True
    fields = ['name', 'bland', 'capacity', 'size', 'type', 'color_category']

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 0
        if obj:
            max_num = obj.item_set.count()
        return max_num

class ItemFeeCoefInline(admin.TabularInline):
    model = models.ItemFeeCoef
    can_delete = True
    show_change_link = False

    def get_extra(self, request, obj=None, **kwargs):
        extra = 3
        if obj:
            return extra - obj.item_fee_coef_set.count()
        return extra

class ItemImageInline(admin.TabularInline):
    model = models.ItemImage
    can_delete = True
    show_change_link = True
    exclude = ['description']

    def get_extra(self, request, obj=None, **kwargs):
        extra = 5
        if obj:
            return extra - obj.item_image_set.count()
        return extra

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 10
        return max_num

class ReservationInline(admin.TabularInline):
    model = models.Reservation
    extra = 0
    can_delete = True
    show_change_link = True
    exclude = ['size', 'type', 'zip_code', 'address', 'name', 'item_fee', 'postage']

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 0
        if obj:
            max_num = obj.reservation_set.count()
        return max_num



class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'min_days', 'max_days')
    list_filter = ['min_days']
    search_fields = ['name', 'description', 'min_days', 'max_days']
    inlines = [ItemInline]

class TypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ['name', 'description']
    inlines = [ItemInline]

class ColorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ['name', 'description']
    inlines = [ItemInline]

class BlandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ['name', 'description']
    inlines = [ItemInline]

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'bland', 'capacity', 'size', 'type', 'color_category', 'color')
    list_filter = ['size', 'type', 'color_category', 'bland']
    search_fields = ['name', 'description', 'bland__name', 'bland__name', 'size__name', 'type__name', 'color_category__name', 'color']
    inlines = [ItemFeeCoefInline, ItemImageInline, ReservationInline]

class LINEUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'line_id', 'zip_code', 'address')
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'line_id', 'zip_code', 'address']
    inlines = [ReservationInline]

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'total_fee', 'start_date', 'return_date', 'address', 'status')
    list_filter = ['start_date', 'return_date', 'item__bland', 'status']
    search_fields = ['name', 'zip_code' 'address', 'size', 'type', 'line_user__name' 'item__name', 'item__bland__name', 'item__color__name']



admin.site.register(models.Size, SizeAdmin)
admin.site.register(models.Type, TypeAdmin)
admin.site.register(models.ColorCategory, ColorCategoryAdmin)
admin.site.register(models.Bland, BlandAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.LINEUser, LINEUserAdmin)
admin.site.register(models.Reservation, ReservationAdmin)
