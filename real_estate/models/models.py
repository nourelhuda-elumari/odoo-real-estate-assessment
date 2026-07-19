from odoo import models, fields, api


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date()
    expected_price = fields.Float(required=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )

    # What kind of property this is (House, Apartment, Villa...).
    # Many2one because a property is only ever ONE type at a time.
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")

    # Every offer that's ever been made on this property. Doesn't
    # add a real column here — Odoo fetches every offer whose
    # property_id points back to this record.
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # The highest price anyone has offered so far. Computed, not
    # typed in — recalculates automatically whenever an offer is
    # added, removed, or its price changes.
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for property in self:
            # max() on an empty list crashes, so default to 0 when
            # there are no offers yet.
            property.best_price = max(property.offer_ids.mapped("price"), default=0.0)


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    # A clean, consistent list of property kinds (House, Apartment,
    # Villa...) instead of everyone typing free text differently.
    name = fields.Char(required=True)


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