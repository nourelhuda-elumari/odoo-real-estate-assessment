from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    # A clean, consistent list of property kinds (House, Apartment,
    # Villa...) instead of everyone typing free text differently.
    name = fields.Char(required=True)

    # Prevents creating "House" twice by accident, which would just
    # confuse the dropdown with duplicate-looking entries.
    #
    # NOTE: this UNIQUE constraint is case-sensitive at the database
    # level, so "Villa" and "villa" would still both be accepted as
    # "different" values. The Python constraint below catches that
    # case too.
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)',
         'A property type with this name already exists.'),
    ]

    @api.constrains('name')
    def _check_name_unique_case_insensitive(self):
        for record in self:
            if not record.name:
                continue
            duplicate = self.search([
                ('id', '!=', record.id),
                ('name', '=ilike', record.name.strip()),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    "A property type named '%s' already exists. "
                    "Property type names must be unique (regardless of upper/lower case)."
                    % record.name
                )