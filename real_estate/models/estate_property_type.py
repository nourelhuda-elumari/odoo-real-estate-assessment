from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    # A clean, consistent list of property kinds (House, Apartment,
    # Villa...) instead of everyone typing free text differently.
    name = fields.Char(required=True)

    # Prevents creating "House" twice by accident, which would just
    # confuse the dropdown with duplicate-looking entries.
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)',
         'A property type with this name already exists.'),
    ]