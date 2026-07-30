from odoo import models, fields


class EstatePropertyImage(models.Model):
    _name = "estate.property.image"
    _description = "Photo of a Real Estate Property"
    _order = "sequence, id"

    name = fields.Char(string="Caption")
    sequence = fields.Integer(default=10)
    image = fields.Image(string="Photo", required=True, max_width=1920, max_height=1920)
    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade")