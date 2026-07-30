from odoo import models, fields


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offer made on a Real Estate Property"

    # The amount the buyer is offering.
    price = fields.Float()

    # Who's making this offer. Reusing res.partner (Odoo's built-in
    # contacts model) instead of a plain text name, so we get
    # email/phone/address for free.
    partner_id = fields.Many2one("res.partner", required=True)

    # Left empty = still pending, no decision made yet.
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )

    # Every offer belongs to exactly ONE property. This Many2one is
    # what makes offer_ids (the One2many above) actually work.
    property_id = fields.Many2one("estate.property", required=True)

    # An offer of 0 or negative money is meaningless.
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)',
         'The offer price must be strictly positive.'),
    ]

    def action_accept(self):
        # Accepting an offer should actually mean something: the
        # property's selling price becomes this offer's price, and
        # since a property can only be sold to one buyer, every
        # other offer on the same property gets auto-refused.
        for offer in self:
            other_offers = offer.property_id.offer_ids - offer
            other_offers.write({"status": "refused"})

            offer.status = "accepted"
            offer.property_id.selling_price = offer.price

    def action_refuse(self):
        for offer in self:
            offer.status = "refused"