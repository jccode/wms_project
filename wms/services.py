# -*- coding: utf-8 -*-

from models import StoreItem

def is_product_exist_in_warehouse(warehouse, product):
    """
    Check if the product exist in warehouse
    Arguments:
    - `warehouse`:
    - `product`:
    """
    storeitems = StoreItem.objects.filter(warehouse=warehouse, product=product)
    return storeitems.count() > 0
        

def update_product_to_warehouse(storein):
    """
    """
    for storeindetail in storein.storeindetail_set.all():
        product = storeindetail.product
        warehouse = storeindetail.warehouse
        if(is_product_exist_in_warehouse(warehouse, product)):
            # update quantity
            storeItem = StoreItem.objects.find_by_warehouse_and_product(warehouse, product)
            storeItem.quantity = storeItem.quantity + storeindetail.quantity
            # storeItem.in_stock_time = timezone.now()
            storeItem.save(update_fields=['quantity',])
        else:
            # create a new StoreItem
            storeItem = StoreItem.from_store_in_detail(storeindetail)
            storeItem.save()  

    
