from odoo import models

# sale_order_line_sequence shows the number of the originating sale order line
# on the invoice, as "SO Line Number". Its compute ends in
#
#     rec.related_so_sequence = str(rec.sale_line_ids.visible_sequence)
#
# and for an invoice line without a sale order line that recordset is empty.
# Odoo answers a field read on an empty recordset with the null value of the
# field type, and Integer.convert_to_record returns "value or 0", so the column
# reads a literal "0" instead of staying blank. This hits manual invoices, and
# section and note lines on every invoice.


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _compute_related_so_sequence(self):
        super()._compute_related_so_sequence()
        for line in self:
            if not line.sale_line_ids:
                line.related_so_sequence = ""
