from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    # Monthly rent, for properties offered for rent instead of / alongside sale.
    rent_price = fields.Float(string="Monthly Rent")

    # A Google Maps URL pointing at the property's location. Paste a
    # "Share location" link copied from Google Maps. Rendered clickable
    # in the form/kanban views via widget="url".
    google_map_link = fields.Char(string="Google Maps Link")

    # Main/cover photo. fields.Image handles resizing/storage automatically.
    image_1920 = fields.Image(string="Main Photo", max_width=1920, max_height=1920)

    # Extra photos (gallery). One2many to a lightweight image-holder model,
    # same pattern Odoo uses for multi-photo galleries elsewhere.
    property_image_ids = fields.One2many(
        "estate.property.image", "property_id", string="Photos"
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

    # ------------------------------------------------------------------
    # SQL constraints — enforced directly by the database, best for
    # simple single-field checks. Each tuple = (internal name, SQL
    # CHECK condition, error message shown to the user).
    # ------------------------------------------------------------------
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
         'The expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
         'The selling price must be positive.'),
        ('check_bedrooms', 'CHECK(bedrooms >= 0)',
         'The number of bedrooms cannot be negative.'),
        ('check_living_area', 'CHECK(living_area >= 0)',
         'The living area cannot be negative.'),
        ('check_facades', 'CHECK(facades >= 0)',
         'The number of facades cannot be negative.'),
        ('check_garden_area', 'CHECK(garden_area >= 0)',
         'The garden area cannot be negative.'),
        ('check_rent_price', 'CHECK(rent_price >= 0)',
         'The monthly rent cannot be negative.'),
    ]

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for property in self:
            # max() on an empty list crashes, so default to 0 when
            # there are no offers yet.
            property.best_price = max(property.offer_ids.mapped("price"), default=0.0)

    # ------------------------------------------------------------------
    # Python constraints — for rules that need to compare multiple
    # fields or need custom logic that plain SQL can't express well.
    # ------------------------------------------------------------------

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            # Only check once a real selling price has been entered —
            # otherwise every unsold property (selling_price = 0.0)
            # would fail this check immediately.
            if record.selling_price and record.selling_price < 0.9 * record.expected_price:
                raise ValidationError(
                    "The selling price cannot be lower than 90% of the expected price. "
                    "You must reduce the expected price if you want to accept this offer."
                )

    @api.constrains('garden', 'garden_area', 'garden_orientation')
    def _check_garden_consistency(self):
        for record in self:
            # If there's no garden, there shouldn't be a garden area
            # or orientation set — that data would be misleading.
            if not record.garden and (record.garden_area or record.garden_orientation):
                raise ValidationError(
                    "A property without a garden cannot have a garden area or orientation."
                )