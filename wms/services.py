# -*- coding: utf-8 -*-

from models import StoreItem

def isProductExistInWarehouse(warehouse, product):
    """
    Check if the product exist in warehouse
    Arguments:
    - `warehouse`:
    - `product`:
    """
    storeitems = StoreItem.objects.filter(warehouse=warehouse, product=product)
    return storeitems.count() > 0
        
