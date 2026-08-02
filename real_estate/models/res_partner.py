from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    # No _name means we are NOT creating a new model —
    # we're adding this field directly onto the existing
    # res.partner table.
    property_offer_ids = fields.One2many(
        "estate.property.offer", "partner_id", string="Property Offers"
    )