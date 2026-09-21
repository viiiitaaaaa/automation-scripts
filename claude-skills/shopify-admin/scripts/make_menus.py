"""Меню магазина: About в шапке, Information и Legal для футера.

Track order добавится сюда же, когда будет ссылка на страницу отслеживания.
"""
from shop_api import gql

MENUS = gql("{ menus(first:20){ nodes{ id handle title items{ id title type url resourceId } } } }")["menus"]["nodes"]
BY_HANDLE = {m["handle"]: m for m in MENUS}

CREATE = """
mutation($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { handle items { title } } userErrors { field message }
  }
}
"""
UPDATE = """
mutation($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
    menu { handle items { title } } userErrors { field message }
  }
}
"""


def item(title, url):
    return {"title": title, "type": "HTTP", "url": url}


def upsert(handle, title, items):
    if handle in BY_HANDLE:
        res = gql(UPDATE, {"id": BY_HANDLE[handle]["id"], "title": title,
                           "handle": handle, "items": items})["menuUpdate"]
    else:
        res = gql(CREATE, {"title": title, "handle": handle, "items": items})["menuCreate"]
    if res["userErrors"]:
        print("ошибка:", handle, res["userErrors"])
    else:
        print(f"{handle:14} ->", [i["title"] for i in res["menu"]["items"]])


# Шапка: к существующим пунктам добавляем About us
upsert("main-menu", "Main menu", [
    item("Home", "/"),
    item("Catalog", "/collections/all"),
    item("Collections", "/collections"),
    item("About us", "/pages/about-us"),
    item("Contact", "/pages/contact"),
])

# Первая колонка футера: справочная информация для покупателя
upsert("information", "Information", [
    item("Frequently asked questions", "/pages/faq"),
    item("About us", "/pages/about-us"),
    item("Contact us", "/pages/contact"),
])

# Вторая колонка футера: правовые документы
upsert("footer", "Footer menu", [
    item("Payment policy", "/pages/payment-policy"),
    item("Shipping policy", "/policies/shipping-policy"),
    item("Refund policy", "/policies/refund-policy"),
    item("Privacy policy", "/policies/privacy-policy"),
    item("Terms of service", "/policies/terms-of-service"),
    item("Search", "/search"),
])
