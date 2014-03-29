# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import TextInput
from django.utils.encoding import smart_unicode
from django.utils.html import conditional_escape, mark_safe
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from wms.models import Client, Warehouse, Category, Product, StoreItem, StoreIn, StoreOut, StoreInDetail, StoreOutDetail


class CategoryFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the right sidebar just above the filter option
    title = _('category')
    
    # parameter for the filter that will be used in the URL query
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. 
        The first element in each tuple is the coded vlue for the option that will appear in the URL query.
        The second element is the human-readable name for the option that will appear in the right sidebar.
        """
        categories = Category.objects.all()
        results = []
        for category in categories:
            results.append((category.id, self._get_name(category)))

        return results

    def queryset(self, request, queryset):
        """
        Filter list by displaying children if parent node has any
        """
        if self.value():
            t = Category.objects.get(id=self.value())
            # return queryset.filter(category__lft__gte=t.lft, category__rght__lte=t.rght)
            # return queryset.filter((Q(category__level=0) & Q(category__tree_id=t.tree_id)) | ~Q(category__level=0), 
            #     category__lft__gte=t.lft, category__rght__lte=t.rght)
            return queryset.filter(category__lft__gte=t.lft,
                category__rght__lte=t.rght,
                category__tree_id=t.tree_id)
        else:
            return queryset

    def _get_name(self, obj):
        """
        Get name with level indicator
        """
        level_indicator = '--- '
        return mark_safe(u'%s%s' % (level_indicator*obj.level, conditional_escape(smart_unicode(obj))))
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'unit')
    # list_filter = ('category', )
    list_filter = (CategoryFilter, )

    



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
admin.site.register(Product, ProductAdmin)
admin.site.register(StoreItem, StoreItemAdmin)  # TODO:只允许查看;不允许修改;
admin.site.register(StoreIn, StoreInAdmin)
admin.site.register(StoreOut, StoreOutAdmin)
