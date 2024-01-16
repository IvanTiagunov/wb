from string import Template

ALL_CATEGORIES = "https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json"

_NOMS_TEMPLATE = "https://catalog.wb.ru/catalog/$shard/catalog?TestGroup=no_test&TestID=no_test&appType=1&" \
               "$cat" \
               "&curr=rub&dest=-2133466&" \
               "page=$page_number&" \
               "sort=popular&spp=27&uclusters=1"

# $shard $cat $page_number поля из базы данных.
# Подставляются при помощи NOMS.substitute(shard, cat, page_number)
NOMS = Template(_NOMS_TEMPLATE)

# $NM подстановка артикула
QNT_TEMPLATE = "https://card.wb.ru/cards/detail?spp=0&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48" \
               "&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,12,7,3,6,13,21" \
               "&dest=-1113276,-79379,-1104258,-5818883" \
               "&nm=$NM"
QNT = Template(QNT_TEMPLATE)


