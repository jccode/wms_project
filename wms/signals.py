# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from models import StoreIn, StoreInDetail, StoreOut, StoreOutDetail
from services import *


# @receiver(post_save, sender=StoreInDetail, dispatch_uid="store_in_post_save_identifier")
def store_in_post_save(sender, **kwargs):
    """
    添加入库单(入库操作)时, 更新库存状态/或者添加新的产品到仓库

    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    storeindetail = kwargs['instance']
    product = storeindetail.product
    warehouse = storeindetail.warehouse
    if(is_product_exist_in_warehouse(warehouse, product)):
        # update quantity
        storeItem = StoreItem.objects.findByWarehouseAndProduct(warehouse, product)
        storeItem.quantity = storeItem.quantity + storeindetail.quantity
        # storeItem.in_stock_time = timezone.now()
        storeItem.save(update_fields=['quantity',])
        
    else:
        # create a new StoreItem
        storeItem = StoreItem.fromStoreInDetail(storeindetail)
        storeItem.save()    



@receiver(post_delete, sender=StoreIn, dispatch_uid='store_in_post_delete_identifier')
def store_in_post_delete(sender, **kwargs):
    """
    当删除一张入库单时, 更新库存的状态

    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    pass
    


@receiver(post_save, sender=StoreOut, dispatch_uid='store_out_post_save_identifier')
def store_out_post_save(sender, **kwargs):
    """
    添加出库单(出库操作)时, 更新库存状态.

    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    pass



@receiver(post_delete, sender=StoreOut, dispatch_uid='store_out_post_delete_identifier')
def store_out_post_delete(sender, **kwargs):
    """
    删除出库单时,同时更新库存状态.

    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    pass


