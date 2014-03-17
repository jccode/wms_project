# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from wms.models import Client, Warehouse, Category, Product, StoreItem, StoreIn, StoreOut, StoreInDetail, StoreOutDetail



class StoreInDetailInline(admin.TabularInline):
    model = StoreInDetail
    extra = 1
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'15'})}
    }
    

class StoreInAdmin(admin.ModelAdmin):
    inlines = [StoreInDetailInline]
        

class StoreOutDetailInline(admin.TabularInline):
    model = StoreOutDetail
    extra = 0


class StoreOutAdmin(admin.ModelAdmin):
    inlines = [StoreOutDetailInline]
        

    
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity', 'area', 'shelf',
        'place', 'format_in_stock_time')
    list_display_links = ('product', )
    readonly_fields = ('in_stock_time', 'warehouse', 'product')
    list_filter = ('warehouse', )
    search_fields = ('product__name', 'in_stock_time')

    def format_in_stock_time(self, obj):
        return obj.in_stock_time.strftime('%Y-%m-%d %H:%M')
    format_in_stock_time.short_description = _('In stock time')
    format_in_stock_time.admin_order_field = 'in_stock_time'
    

admin.site.register(Client)
admin.site.register(Warehouse)
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Product)
admin.site.register(StoreItem, StoreItemAdmin)  # TODO:只允许查看;不允许修改;
admin.site.register(StoreIn, StoreInAdmin)
admin.site.register(StoreOut, StoreOutAdmin)
