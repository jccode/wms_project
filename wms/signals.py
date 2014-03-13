# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from models import StoreIn, StoreOut


@receiver(post_save, sender=StoreIn, dispatch_uid="store_in_post_save_identifier")
def store_in_post_save(sender, **kwargs):
    """
    添加入库单(入库操作)时, 更新库存状态/或者添加新的产品到仓库

    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    # print "store in post save. item: %s" % unicode(sender)
    # print kwargs
    instance = kwargs['instance'] # StockIn instance
    


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


