# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import models as auth
from django.utils import timezone
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Client(models.Model):
    
    TYPE = (
        (1, _('Supplier')), 
        (2, _('Buyer')), 
    )

    number = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    type = models.IntegerField(choices=TYPE)
    contact = models.CharField(max_length=45)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=45)
    postcode = models.CharField(max_length=10)
    fax = models.CharField(max_length=20)
    remark = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')

    def __unicode__(self):
        return self.name
        

class Warehouse(models.Model):
    number = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    remark = models.CharField(max_length=200, blank=True)
    admin = models.ForeignKey(auth.User)

    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')

    def __unicode__(self):
        return self.name

        
class Category(MPTTModel):
    number = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categorys')

    def __unicode__(self):
        return self.name


class Product(models.Model):
    number = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    spec = models.CharField(max_length=45, verbose_name=_('Specification'), blank=True)
    barcode = models.CharField(max_length=45, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=45)
    category = TreeForeignKey(Category)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    
    def __unicode__(self):
        return self.name


class StoreItemManager(models.Manager):
    def findByWarehouseAndProduct(self, warehouse, product):
        """
        
        Arguments:
        - `warehouse`:
        - `Product`:
        """
        items = self.filter(warehouse=warehouse, product=product)
        if items.count() > 0:
            return items[0]
        return None
        

class StoreItem(models.Model):
    warehouse = models.ForeignKey(Warehouse)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    area = models.CharField(max_length=45, blank=True, verbose_name=_('Area'))
    shelf = models.CharField(max_length=45, blank=True, verbose_name=_('Shelf'))
    place = models.CharField(max_length=45, blank=True, verbose_name=_('Place'))
    in_stock_time = models.DateTimeField(_('In stock time'))
    objects = StoreItemManager()

    class Meta:
        ordering = ['-in_stock_time']
        verbose_name = _('Stock Item')
        verbose_name_plural = _('Stock Items')

    @classmethod
    def fromStoreInDetail(cls, storeInDetail):
        return StoreItem(warehouse = storeInDetail.warehouse,
            product = storeInDetail.product,
            quantity = storeInDetail.quantity,
            area = storeInDetail.area,
            shelf = storeInDetail.shelf,
            place = storeInDetail.place,
            in_stock_time = timezone.now())
        
    def __unicode__(self):
        return '[%d %s in %s]' % (self.quantity, unicode(self.product), unicode(self.warehouse))

        

class StoreIn(models.Model):

    TYPE = (
        (1, _('purchase')),     # 采购入库
        (2, _('production')),   # 生产入库
        (3, _('return product')), # 退货入库
        (4, _('return material in')), # 退料入库
    )
    
    number = models.CharField(max_length=45)
    type = models.IntegerField(choices=TYPE)
    create_time = models.DateTimeField()
    complete_time = models.DateTimeField()
    approver = models.ForeignKey(auth.User, related_name="+", verbose_name=_('Approver')) # 接收人
    deliver = models.CharField(max_length=45, verbose_name=_('Deliver')) # 送货人
    recipient = models.ForeignKey(auth.User, related_name="+", verbose_name=_('Recipient')) # 核准人
    
    class Meta:
        verbose_name = _('Stock In Record')
        verbose_name_plural = _('Stock In Records')

    def __unicode__(self):
        return '[%s, %s, %s]' % (self.number, self.TYPE[self.type][1], unicode(self.create_time))
        
    

class StoreInDetail(models.Model):
    store_in = models.ForeignKey(StoreIn)
    warehouse = models.ForeignKey(Warehouse)
    client = models.ForeignKey(Client)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    area = models.CharField(max_length=45, blank=True, verbose_name=_('Area'))
    shelf = models.CharField(max_length=45, blank=True, verbose_name=_('Shelf'))
    place = models.CharField(max_length=45, blank=True, verbose_name=_('Place'))

    def __unicode__(self):
        return '[%d %s %s into %s]' % (self.quantity, unicode(self.client), unicode(self.product), unicode(self.warehouse))
        
    
    
class StoreOut(models.Model):

    TYPE = (
        (1, _('sale')),     # 销售出库
        (2, _('consume material')),  # 用料出库
        (3, _('return material out')),   # 退料出库
    )
    
    number = models.CharField(max_length=45)
    type = models.IntegerField(choices=TYPE)
    create_time = models.DateTimeField()
    complete_time = models.DateTimeField()
    approver = models.ForeignKey(auth.User, related_name="+", verbose_name=_('Approver')) # 接收人
    sender = models.CharField(max_length=45, verbose_name=_('Deliver')) # 收货人
    recipient = models.ForeignKey(auth.User, related_name="+", verbose_name=_('Recipient')) # 核准人
    
    class Meta:
        verbose_name = _('Stock Out Record')
        verbose_name_plural = _('Stock Out Records')
    
    def __unicode__(self):
        return '[%s, %s, %s]' % (self.number, self.TYPE[self.type][1], unicode(self.create_time))
      

class StoreOutDetail(models.Model):
    store_out = models.ForeignKey(StoreOut)
    warehouse = models.ForeignKey(Warehouse)
    client = models.ForeignKey(Client)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()

    def __unicode__(self):
        return '[%d %s issued from %s to %s]' % (self.quantity, unicode(self.product), unicode(self.warehouse), unicode(self.client))
        
        

        
####################
import signals
####################

from signals import *
