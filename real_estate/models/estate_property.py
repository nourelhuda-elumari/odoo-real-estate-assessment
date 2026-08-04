from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


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

    # A Google Maps URL pointing at the property's location.
    google_map_link = fields.Char(string="Google Maps Link")

    # Main/cover photo.
    image_1920 = fields.Image(string="Main Photo", max_width=1920, max_height=1920)

    # Extra photos (gallery).
    property_image_ids = fields.One2many(
        "estate.property.image", "property_id", string="Photos"
    )

    # Property type selection.
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")

    # Property offers list.
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # The highest price offered so far — stored in DB for Pivot View aggregation.
    best_price = fields.Float(
        compute="_compute_best_price",
        string="Best Offer",
        store=True,
        aggregator="max",
    )

    # Combined living + garden area — stored so it can be searched/sorted.
    total_area = fields.Integer(
        compute="_compute_total_area",
        string="Total Area (m²)",
        store=True,
    )

    # Salesperson handling the property.
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )

    # Property lifecycle status.
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
    )

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
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.constrains('expected_price')
    def _check_expected_price_positive(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("The expected price must be strictly positive.")

    @api.constrains('selling_price')
    def _check_selling_price_positive(self):
        for record in self:
            if record.selling_price < 0:
                raise ValidationError("The selling price cannot be negative.")

    @api.constrains('rent_price')
    def _check_rent_price_positive(self):
        for record in self:
            if record.rent_price < 0:
                raise ValidationError("The monthly rent cannot be negative.")

    @api.constrains('bedrooms', 'living_area', 'facades', 'garden_area')
    def _check_non_negative_integers(self):
        for record in self:
            if record.bedrooms < 0:
                raise ValidationError("The number of bedrooms cannot be negative.")
            if record.living_area < 0:
                raise ValidationError("The living area cannot be negative.")
            if record.facades < 0:
                raise ValidationError("The number of facades cannot be negative.")
            if record.garden_area < 0:
                raise ValidationError("The garden area cannot be negative.")

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price and record.selling_price < 0.9 * record.expected_price:
                raise ValidationError(
                    "The selling price cannot be lower than 90% of the expected price. "
                    "You must reduce the expected price if you want to accept this offer."
                )

    @api.constrains('garden', 'garden_area', 'garden_orientation')
    def _check_garden_consistency(self):
        for record in self:
            if not record.garden and (record.garden_area or record.garden_orientation):
                raise ValidationError(
                    "A property without a garden cannot have a garden area or orientation."
                )

    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise UserError("A canceled property cannot be marked as sold.")
            record.state = "sold"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("A sold property cannot be canceled.")
            record.state = "canceled"
        return True