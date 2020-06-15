# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_is_zero, pycompat
from odoo.tools.pdf import merge_pdf
from odoo.addons import decimal_precision as dp
from datetime import date
import os
import io
import base64
from collections import defaultdict
from PyPDF2 import PdfFileMerger


class AccountMove(models.Model):
    _inherit = 'account.move'

    print_report = fields.Binary('Printed report')

    def print_report_binary(self):
        self.ensure_one()
        pdf = self.env.ref('l10n_ar_report_fe.account_fe_invoices').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        self.write({'print_report': b64_pdf})
        #return self.env('sale.action_report_saleorder').report_action(self)

class AccountMultiPrint(models.Model):
    _name = 'account.multi.print'
    _description = 'account.multi.print'

    def generate_multi_report(self):
        self.ensure_one()
        if not self.print_report and self.account_move_ids:
            for account_move in self.account_move_ids:
                account_move.print_report_binary()
            # merger = PdfFileMerger(strict=False)
            reports = []
            for account_move in self.account_move_ids:
                if account_move.print_report:
                    #raise ValidationError(type(account_move.print_report))
                    #if account_move.print_report.startswith(b'%PDF-'):
                    #    raise ValidationError('estamos mal pero vgamos bien')
                    #f = io.BytesIO(account_move.print_report)
                    #f = io.BytesIO(base64.b64decode(account_move.print_report))
                    f = base64.b64decode(account_move.print_report)
                    reports.append(f)
                    # merger.append(f,import_bookmarks=False)
                    #merger.append(base64.encodestring(account_move.print_report),import_bookmarks=False)
            #output = open('/tmp/salida_facturas.pdf','w+')
            #merger.write(output)
            #output.close()
            merged_pdf = merge_pdf(reports)
            self.print_report = base64.b64encode(merged_pdf)

    name = fields.Char('Nombre')
    account_move_ids = fields.Many2many(comodel_name='account.move',relname='account_multi_rel',column1='print_id',column2='move_id',string='Facturas')
    print_report = fields.Binary('Archivo generado')

#class PurchaseOrder(models.Model):
#	_inherit = 'purchase.order'
#
#	def button_confirm(self):
#		res = super(PurchaseOrder, self).button_confirm()
#		for rec in self:
#			for line in rec.order_line:
#				product_tmpl = line.product_id.product_tmpl_id
#				product_tmpl.with_context(force_company=rec.company_id.id).write({'standard_price': line.price_unit})
#		return res

