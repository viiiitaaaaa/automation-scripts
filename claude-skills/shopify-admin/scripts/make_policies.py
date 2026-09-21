# -*- coding: utf-8 -*-
"""Заливка трёх политик магазина. Сроки согласованы со страницей FAQ."""
import json
from shop_api import gql

SHIPPING = """
<p>All orders are shipped from our fulfilment partners with tracking included. Shipping is
free to the United Kingdom, the European Union and the United States.</p>

<h3>Dispatch</h3>
<p>Orders are dispatched within two working days. You will receive a confirmation email with
a tracking number as soon as the parcel leaves the warehouse; the number usually starts
updating two to four days later. You can follow your parcel at any time on our
<a href="/pages/track-order">order tracking page</a>.</p>

<h3>Delivery times</h3>
<ul>
<li>United Kingdom — 7 to 14 working days</li>
<li>European Union — 7 to 14 working days</li>
<li>United States — 10 to 18 working days</li>
</ul>
<p>Delivery times are estimates and do not include the dispatch period. Customs checks,
public holidays and peak seasons can add a few days.</p>

<h3>Duties and taxes</h3>
<p>Prices shown at checkout include all applicable taxes for the destination we ship to. You
will not be asked to pay anything on delivery.</p>

<h3>Multiple items</h3>
<p>Pieces in one order may be shipped separately and arrive on different days. Each parcel
has its own tracking number.</p>

<h3>Incorrect or incomplete addresses</h3>
<p>Please check your address carefully at checkout. If a parcel is returned to us because the
address was wrong or incomplete, we will re-send it once you confirm the correct details.</p>

<h3>Delays and lost parcels</h3>
<p>If tracking has not moved for 10 working days, or your parcel has not arrived within 30
working days of dispatch, write to <a href="mailto:store@artmellio.com">store@artmellio.com</a>
and we will trace it, replace it or refund it in full.</p>

<p>Questions about a delivery: <a href="mailto:store@artmellio.com">store@artmellio.com</a>.</p>
"""

REFUND = """
<p>If a piece is not right for your home, you can return it within 14 days of delivery.</p>

<h3>Returns</h3>
<p>To start a return, write to <a href="mailto:store@artmellio.com">store@artmellio.com</a>
with your order number within 14 days of receiving your order. We will reply with return
instructions and the return address. Please do not send anything back before contacting us —
parcels returned without instructions cannot be traced to your order.</p>

<p>To be accepted, an item must be unused, in the same condition in which you received it, and
in its original packaging. Natural stone varies in colour, veining and pattern from piece to
piece; this is a property of the material and not a defect.</p>

<h3>Return shipping</h3>
<p>Return postage is paid by the customer, except where the item arrived damaged, faulty or
was not what you ordered — in those cases we cover the cost in full.</p>

<h3>Damaged or faulty items</h3>
<p>Send a photograph to <a href="mailto:store@artmellio.com">store@artmellio.com</a> within
48 hours of delivery and we will replace the piece or refund it in full. Stone travels well,
but corners can chip in transit, and we would rather put it right than have you keep
something imperfect.</p>

<h3>Refunds</h3>
<p>Once your return has been received and checked, we will email you with the outcome and
refund the original payment method within 5 to 10 working days. Depending on your bank, the
money can take a few further days to appear on your statement. Where a discount was applied
to a set, the refund is calculated on the amount actually paid for the returned item.</p>

<h3>Cancellations</h3>
<p>An order can be cancelled free of charge at any time before it is dispatched. Write to us
as soon as possible — once a parcel has left the warehouse it has to be handled as a return.</p>

<h3>Exchanges</h3>
<p>The quickest way to exchange a piece is to return it for a refund and place a new order.</p>
"""

TERMS = """
<p>These terms govern your use of artmellio.com and any purchase made through it. By placing
an order you accept them.</p>

<h3>The store</h3>
<p>ARTMELLIO sells decorative objects made from natural stone. The store is operated from
Poland. Contact: <a href="mailto:store@artmellio.com">store@artmellio.com</a>.</p>

<h3>Products</h3>
<p>We describe every piece as accurately as we can. Because our objects are cut from natural
marble, travertine and onyx, colour, veining and pattern differ from piece to piece, and the
item you receive will not be identical to the photograph. Dimensions are given as accurately
as the material allows and may vary slightly.</p>

<h3>Prices and payment</h3>
<p>Prices are shown in the currency of your region and include applicable taxes. We may change
prices at any time, but never after an order has been confirmed. Payment is taken at checkout
through Shopify's payment providers; we do not see or store your card details.</p>

<h3>Discounts</h3>
<p>Automatic set discounts apply to the order total and are shown in the cart before payment.
Only one tier applies to an order — always the highest one the order qualifies for. Discounts
cannot be exchanged for cash and may be withdrawn or changed for future orders at any time.</p>

<h3>Orders</h3>
<p>An order is an offer to buy. We may decline or cancel an order — for example if an item is
out of stock, if it was listed at an obviously incorrect price, or if we cannot ship to the
address given. If we cancel an order that has been paid for, we refund it in full.</p>

<h3>Delivery, returns and refunds</h3>
<p>Delivery is covered by our <a href="/policies/shipping-policy">Shipping Policy</a>; returns
and refunds by our <a href="/policies/refund-policy">Refund Policy</a>. Both form part of these
terms.</p>

<h3>Your statutory rights</h3>
<p>Nothing in these terms limits the rights you have as a consumer under the law of your
country of residence, including the right to withdraw from a distance purchase.</p>

<h3>Content of this site</h3>
<p>Text, photographs and design on artmellio.com belong to ARTMELLIO and may not be reproduced
for commercial use without written permission.</p>

<h3>Liability</h3>
<p>Our objects are decorative. We are not liable for damage caused by use other than the
intended one, or for damage to surfaces on which an item is placed. Our liability in any case
is limited to the amount you paid for the item.</p>

<h3>Privacy</h3>
<p>How we handle personal data is set out in our
<a href="/policies/privacy-policy">Privacy Policy</a>.</p>

<h3>Changes</h3>
<p>We may update these terms; the version published at the time of your order applies to it.</p>
"""

M = """
mutation($p: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $p) {
    shopPolicy { type url }
    userErrors { field message }
  }
}
"""

for ptype, body in (("SHIPPING_POLICY", SHIPPING),
                    ("REFUND_POLICY", REFUND),
                    ("TERMS_OF_SERVICE", TERMS)):
    r = gql(M, {"p": {"type": ptype, "body": body.strip()}})["shopPolicyUpdate"]
    print(ptype, "->", json.dumps(r, ensure_ascii=False))
