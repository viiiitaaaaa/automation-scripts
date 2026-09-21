"""Добавить в профиль доставки зоны UK и EU с бесплатной доставкой."""
from shop_api import gql

PROFILE = "gid://shopify/DeliveryProfile/132357128572"
GROUP = "gid://shopify/DeliveryLocationGroup/134199968124"

EU = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU",
      "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]

CURRENCY = gql("{ shop { currencyCode } }")["shop"]["currencyCode"]


def zone(name, codes):
    return {
        "name": name,
        # страны с регионами (GB, IT, ES...) Shopify не принимает без явного
        # включения всех провинций
        "countries": [{"code": c, "includeAllProvinces": True} for c in codes],
        "methodDefinitionsToCreate": [{
            "name": "Free shipping",
            "active": True,
            "rateDefinition": {"price": {"amount": "0.0", "currencyCode": CURRENCY}},
        }],
    }


M = """
mutation($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile { id }
    userErrors { field message }
  }
}
"""

res = gql(M, {
    "id": PROFILE,
    "profile": {"locationGroupsToUpdate": [{
        "id": GROUP,
        "zonesToCreate": [zone("United Kingdom", ["GB"]), zone("Europe", EU)],
    }]},
})
print("ошибки:", res["deliveryProfileUpdate"]["userErrors"])

check = gql("""{ deliveryProfiles(first:3){ nodes{ profileLocationGroups{
  locationGroupZones(first:20){ nodes{ zone{ name countries{ code{ countryCode } } }
  methodDefinitions(first:3){ nodes{ name active } } } } } } } }""")
for p in check["deliveryProfiles"]["nodes"]:
    for lg in p["profileLocationGroups"]:
        for z in lg["locationGroupZones"]["nodes"]:
            names = [c["code"]["countryCode"] for c in z["zone"]["countries"]]
            methods = [(m["name"], m["active"]) for m in z["methodDefinitions"]["nodes"]]
            print(f"зона {z['zone']['name']}: стран {len(names)} {names[:6]} | тарифы {methods}")
