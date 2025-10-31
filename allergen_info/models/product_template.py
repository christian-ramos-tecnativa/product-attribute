# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allergen_ids = fields.Many2many(
        comodel_name="allergen.allergen",
        string="Allergens",
        compute="_compute_allergen_ids",
        store=False,
        readonly=False,
        help="Allergens present in this product template. "
        "Note: Different variants may have different allergens.",
    )

    @api.depends("product_variant_ids.allergen_ids")
    def _compute_allergen_ids(self):
        """Compute allergens from variants.
        
        If all variants have the same allergens, show those allergens.
        If variants have different allergens, show the union of all allergens.
        """
        for template in self:
            if template.product_variant_ids:
                # Get allergens from all variants
                all_allergens = template.product_variant_ids.mapped("allergen_ids")
                template.allergen_ids = all_allergens
            else:
                template.allergen_ids = False

    def write(self, vals):
        """Override write to propagate allergen changes to variants."""
        res = super().write(vals)
        if "allergen_ids" in vals and self.product_variant_ids:
            # Only update variants if template has a single variant
            # or if we want to propagate to all variants
            for template in self:
                if len(template.product_variant_ids) == 1:
                    template.product_variant_ids.allergen_ids = template.allergen_ids
        return res
