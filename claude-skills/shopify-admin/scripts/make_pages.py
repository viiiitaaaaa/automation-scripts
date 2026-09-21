"""Создать страницы магазина: About, FAQ, Payment policy."""
from shop_api import gql

ABOUT = """
<p>ARTMELLIO sells objects cut from natural stone — marble, travertine and onyx — for the
places in a home where things are set down: the basin, the dressing table, the hall console,
the shelf beside a bed.</p>

<p>We look for pieces where the material does the work. A tray is a slab with an edge; a
dispenser is a block with a hole bored through it. There is no printing, no marble-effect
film and no logo pressed into the side. What you see on the surface is the stone's own
veining, formed long before it was quarried, which is why the piece that arrives will not
be an exact copy of the photograph on the page.</p>

<p>The catalogue is organised by interior style rather than by room, because that is how
people actually furnish: Neo-Japandi, Warm Minimalism, Organic Luxe, Quiet Luxury,
Sculptural Contemporary, Dark Academia, Heritage Maximalism and Eclectic Collector. Pick
the register your room is already in, and the objects will sit in it without argument.</p>

<p>We ship free to the United Kingdom, the European Union and the United States. Questions
before you order are welcome — the contact page reaches us directly.</p>
"""

FAQ = """
<h3>Ordering and delivery</h3>

<p><strong>How long does delivery take?</strong><br>
Orders are dispatched within two working days. Delivery takes 7–14 working days to the UK
and Europe and 10–18 working days to the United States. A tracking number is sent as soon
as the parcel leaves the warehouse.</p>

<p><strong>Is shipping really free?</strong><br>
Yes — to the United Kingdom, the European Union and the United States, with no minimum
order value. The price shown on the product page is the price you pay at checkout.</p>

<p><strong>Where do you ship from?</strong><br>
Pieces are dispatched directly from our supply partners, which keeps stone at these prices.
That is also why delivery takes longer than a domestic warehouse would.</p>

<p><strong>Can I track my order?</strong><br>
Yes. You receive a tracking number by email once the parcel is dispatched.</p>

<h3>The stone itself</h3>

<p><strong>Why does my piece look different from the photograph?</strong><br>
Marble, travertine and onyx are cut from natural blocks. Veining, tone and the pattern of
the pores change from piece to piece. The photograph shows one example, not the exact item
you will receive.</p>

<p><strong>Is it real stone?</strong><br>
Where a product is listed as marble, travertine or onyx, it is cut stone. Pieces made from
resin, ceramic or stone composite say so in their description.</p>

<p><strong>How do I look after it?</strong><br>
Wipe with a damp cloth and dry. Avoid acidic cleaners, limescale removers and bleach: they
etch polished stone and leave dull patches that cannot be buffed out. Stand perfume and
nail polish on a coaster — solvents mark the surface.</p>

<p><strong>Is stone suitable for a bathroom?</strong><br>
Yes. Splashes are harmless as long as they are wiped up; what damages stone is standing
water and harsh cleaning products.</p>

<h3>Returns</h3>

<p><strong>Can I return an order?</strong><br>
Yes, within 14 days of delivery, provided the piece is unused and in its original packaging.
Write to us and we will send return instructions.</p>

<p><strong>My order arrived damaged.</strong><br>
Send us a photograph within 48 hours of delivery and we will replace the piece or refund it
in full. Stone travels well but corners can chip in transit.</p>
"""

PAYMENT = """
<p>All payments are processed by Shopify Payments over an encrypted connection. We never see
or store your card details.</p>

<h3>Accepted methods</h3>
<ul>
  <li>Visa, Mastercard, Maestro and American Express</li>
  <li>Apple Pay and Google Pay</li>
  <li>Shop Pay, including its instalment option where available in your country</li>
</ul>

<h3>Currency</h3>
<p>Prices are shown in the currency of your region — pounds sterling in the United Kingdom,
euros in the European Union, dollars in the United States. The amount charged is the amount
displayed at checkout. Your bank may add its own conversion fee if your card is issued in a
different currency.</p>

<h3>When you are charged</h3>
<p>Payment is taken at the moment the order is placed. If an item turns out to be unavailable
after that, we refund it in full to the original payment method within five working days.</p>

<h3>Taxes and duties</h3>
<p>Prices include VAT where it applies. Orders shipped outside the United Kingdom and the
European Union may attract import duty on arrival, which is set by the destination country
and is the responsibility of the recipient.</p>

<h3>Failed payments</h3>
<p>If a payment is declined, check the card details and the billing address, then try again.
If it still fails, contact your bank — declines are almost always made on their side, not
ours. You can also write to us and we will help.</p>
"""

PAGES = [
    ("about-us", "About us", ABOUT),
    ("faq", "Frequently asked questions", FAQ),
    ("payment-policy", "Payment policy", PAYMENT),
]

CREATE = """
mutation($page: PageCreateInput!) {
  pageCreate(page: $page) { page { id handle title } userErrors { field message } }
}
"""

existing = {p["handle"] for p in gql("{ pages(first:50){ nodes{ handle } } }")["pages"]["nodes"]}

for handle, title, body in PAGES:
    if handle in existing:
        print("уже есть:", handle)
        continue
    res = gql(CREATE, {"page": {
        "handle": handle,
        "title": title,
        "body": body.strip(),
        "isPublished": True,
    }})["pageCreate"]
    if res["userErrors"]:
        print("ошибка:", handle, res["userErrors"])
    else:
        print("создана:", res["page"]["handle"], "|", res["page"]["title"])
