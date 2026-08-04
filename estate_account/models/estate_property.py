from odoo import models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    # No _name here — we're extending the estate.property model that
    # already exists in the real_estate module, not creating a new one.
    _inherit = "estate.property"

    def action_sold(self):
        # Run the original action_sold logic first (state validation,
        # e.g. blocking canceled properties). If it raises, we never
        # reach the invoicing code below.
        result = super().action_sold()

        for prop in self:
            accepted_offer = prop.offer_ids.filtered(lambda o: o.status == "accepted")
            if not accepted_offer:
                raise UserError(
                    "Cannot create an invoice: this property has no "
                    "accepted offer, so there is no buyer to invoice."
                )
            buyer = accepted_offer[0].partner_id

            self.env["account.move"].create({
                "partner_id": buyer.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (0, 0, {
                        "name": f"6% commission on sale of {prop.name}",
                        "quantity": 1,
                        "price_unit": 0.06 * prop.selling_price,
                    }),
                    (0, 0, {
                        "name": "Administrative fee",
                        "quantity": 1,
                        "price_unit": 100.00,
                    }),
                ],
            })

        return result