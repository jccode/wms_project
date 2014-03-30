# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import TextInput
from django.utils.encoding import smart_unicode, force_text
from django.utils.html import conditional_escape, mark_safe
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from wms.models import Client, Warehouse, Category, Product, StoreItem, StoreIn, StoreOut, StoreInDetail, StoreOutDetail
from wms.utils import ReadonlyTabularInline
from wms.services import update_product_to_warehouse


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

    

class StoreInDetailReadonlyInline(ReadonlyTabularInline):
    model = StoreInDetail
    

    
class StoreInAdmin(admin.ModelAdmin):
    # inlines = [StoreInDetailInline]
    list_display = ('type', 'approver', 'create_time', 'is_approved')
    list_filter = ('is_approved', 'create_time')
    # actions = ['make_approved']
    
    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            kwargs['exclude'] = ['recipient', ]
        return super(StoreInAdmin, self).get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if self.is_readonly(obj):
            readonly_fields = [field.name for field in obj.__class__._meta.fields]
            readonly_fields.remove('id')
            return readonly_fields
            
        return self.readonly_fields
        
    def get_actions(self, request):
        actions = super(StoreInAdmin, self).get_actions(request)
        
        # TODO:: add permission logic
        # if have approve permission
        have_approve_permission = request.user.has_perm('wms.approve')
        if have_approve_permission:
            actions['make_approved'] = self.get_action('make_approved')
        return actions

        
    def make_approved(self, request, queryset):
        queryset = queryset.filter(is_approved=False)
        rows_updated = queryset.update(is_approved=True, recipient=request.user.id)

        # update to warehouse
        for obj in queryset:
            update_product_to_warehouse(obj)

        if rows_updated == 1:
            message_bit = "1 object was"
        else:
            message_bit = "%s objects were" % rows_updated
        self.message_user(request, "%s successfully approved." % message_bit)
    make_approved.short_description = _('Mark selected objects as approved')

    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = StoreIn.objects.get(pk=object_id)
        if self.is_readonly(obj):
            extra_context = extra_context or {}
            extra_context['readonly'] = True
            extra_context['title'] = _('View %s') % force_text(self.model._meta.verbose_name)
        return super(StoreInAdmin, self).change_view(request, object_id, form_url, extra_context)


    def get_inline_instances(self, request, obj=None):
        inlines = []
        if self.is_readonly(obj):
            inlines = [StoreInDetailReadonlyInline, ]
        else:
            inlines = [StoreInDetailInline, ]

        # return inline instances
        return [inline(self.model, self.admin_site) for inline in inlines]

    def has_delete_permission(self, request, obj=None):
        print 'has_delete_permission %s' % unicode(obj)
        if obj and obj.is_approved:
            return False
        return True

    # def my_delete_action(self, request, queryset):
    #     count = 0
    #     for obj in queryset:
    #         if not obj.is_approved:
    #             obj.delete()
    #             count += 1
    #     if count == 1:
    #         message_bit = '1 %s was' % force_text(self.model._meta.verbose_name)
    #     else:
    #         message_bit = '%s %s were' % (count, force_text(self.admin._meta.verbose_name))
    #     self.message_user(request, "%s successfully deleted." % message_bit)
    # my_delete_action.short_description = _('Delete selected entities')
    
    
        
    def is_readonly(self, obj=None):
        return obj and obj.is_approved

        

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
    actions = None

    def format_in_stock_time(self, obj):
        return obj.in_stock_time.strftime('%Y-%m-%d %H:%M')
    format_in_stock_time.short_description = _('In stock time')
    format_in_stock_time.admin_order_field = 'in_stock_time'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

        


admin.site.register(Client)
admin.site.register(Warehouse)
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(StoreItem, StoreItemAdmin)  # TODO:只允许查看;不允许修改;
admin.site.register(StoreIn, StoreInAdmin)
admin.site.register(StoreOut, StoreOutAdmin)
