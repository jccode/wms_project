# -*- coding: utf-8 -*-

from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from wms.models import Client, Warehouse, Category, Product, StoreItem, StoreIn, StoreOut, StoreInDetail, StoreOutDetail


class StoreInDetailInline(admin.TabularInline):
    model = StoreInDetail
    extra = 1
    

class StoreInAdmin(admin.ModelAdmin):
    inlines = [StoreInDetailInline]
        

class StoreOutDetailInline(admin.TabularInline):
    model = StoreOutDetail
    extra = 0


class StoreOutAdmin(admin.ModelAdmin):
    inlines = [StoreOutDetailInline]
        
        
    

admin.site.register(Client)
admin.site.register(Warehouse)
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Product)
admin.site.register(StoreItem)  # TODO:只允许查看;不允许修改;
admin.site.register(StoreIn, StoreInAdmin)
admin.site.register(StoreOut, StoreOutAdmin)
