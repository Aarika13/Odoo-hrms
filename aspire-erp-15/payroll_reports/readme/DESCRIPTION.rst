Add this pyton code in your model for net amount in words:

    total_in_words = fields.Char(compute='_compute_total_in_words', string='Total In Words')

    @api.depends('total')

    def _compute_total_in_words(self):
        for line in self:
            line.total_in_words = num2words(line.total)

    Where 'total' field contains total amount in number.