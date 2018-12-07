Get top 10 products:

```
from saleboxdjango.lib.product_list import ProductList

pl = ProductList()
pl.set_limit_offset(10)
pl.set_order_preset('rating_high_to_low')
products = pl.go()
```

Get page of products:
(page #1, 40 per page)

```
from saleboxdjango.lib.product_list import ProductList

pl = ProductList()
pl.set_pagination(1, 40)
pl.set_order_preset('price_low_to_high')
products = pl.go()
```
