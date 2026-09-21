"""Переписать тексты чекаута: они правятся как переводы темы.

Ключи вида shopify.checkout.* лежат в ONLINE_STORE_THEME. Для записи нужен digest
исходной строки — иначе Shopify не примет перевод.
"""
from shop_api import gql

NEW = {
    # «OR» над альтернативными способами оплаты ничего не объясняет
    "shopify.checkout.alternative_payment_method_banner.or": "OR CONTINUE WITH YOUR CARD",
    # галочку про новости не отмечают; отслеживание заказа — понятная причина
    "shopify.checkout.marketing.accept_marketing_checkbox_label":
        "Email me about my order and new arrivals",
    # доставка бесплатная, и сказать об этом надо до ввода адреса
    "shopify.checkout.shipping_errors.empty_state":
        "Free delivery with tracking. Enter your shipping address to see the options.",
    "shopify.checkout.payment_gateway.credit_card_label": "Debit or credit card",
}

Q = """
query($rt: TranslatableResourceType!) {
  translatableResources(first: 5, resourceType: $rt) {
    nodes { resourceId translatableContent { key value digest locale } }
  }
}
"""
M = """
mutation($id: ID!, $translations: [TranslationInput!]!) {
  translationsRegister(resourceId: $id, translations: $translations) {
    translations { key value }
    userErrors { field message }
  }
}
"""

node = gql(Q, {"rt": "ONLINE_STORE_THEME"})["translatableResources"]["nodes"][0]
by_key = {c["key"]: c for c in node["translatableContent"]}

items = []
for key, value in NEW.items():
    src = by_key.get(key)
    if not src:
        print("ключ не найден:", key)
        continue
    print(f"{key}\n   было: {src['value']!r}\n   стало: {value!r}")
    items.append({
        "key": key,
        "value": value,
        "locale": src["locale"],
        "translatableContentDigest": src["digest"],
    })

res = gql(M, {"id": node["resourceId"], "translations": items})["translationsRegister"]
print("\nзаписано:", len(res["translations"]), "| ошибки:", res["userErrors"])
