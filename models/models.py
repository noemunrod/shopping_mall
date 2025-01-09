# -*- coding: utf-8 -*-
"""Odoo module for Shopping shopping activities"""
from datetime import date
from odoo import api, fields, models  # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


class IrCron(models.Model):
    """Management of different cron tasks"""
    _inherit = 'ir.cron'

    @api.model
    def create_deactivate_expired_prices(self):
        """Creates the cron task for deactivating the expired prices"""
        self.create({
            'name': 'Deactivate Expired Prices',
            'model_id': self.env.ref('shopping_mall.model_shopping_mall_price').id,
            'state': 'code',
            'code': 'model.deactivate_expired_prices()',
            'interval_type': 'minutes',
            'interval_number': 60,
            "active": True,
        })

    @api.model
    def create_activate_current_prices(self):
        """Creates the cron task for activating the current prices"""
        self.create({
            'name': 'Activate Current Prices',
            'model_id': self.env.ref('shopping_mall.model_shopping_mall_price').id,
            'state': 'code',
            'code': 'model.activate_current_prices()',
            'interval_type': 'minutes',
            'interval_number': 60,
            "active": True,
        })


class Price(models.Model):
    """Price entity with status and timestamps of activation"""
    _name = 'shopping_mall.price'
    _description = 'Collection of prices, activated and not'

    price = fields.Float('Price')
    date_starts = fields.Datetime('Start Date')
    date_ends = fields.Datetime('End Date')
    active = fields.Boolean('Active', default=True)
    product_id = fields.Many2one('shopping_mall.product', string='Product')

    @api.model
    def deactivate_expired_prices(self):
        """Deactivate the prices that have passed their expiration date"""
        current_date = fields.Datetime.now()
        expired_prices = self.search([
            ('date_ends', '<', current_date),
            ('active', '=', True)
        ])

        for price in expired_prices:
            price.active = False

    @api.model
    def activate_current_prices(self):
        """Activate the prices for the current date"""
        current_date = fields.Datetime.now()
        current_prices = self.search([
            ('date_starts', '>=', current_date),
            ('active', '=', False)
        ])
        for price in current_prices:
            price.active = True

    @api.constrains('active', 'product_id')
    def _check_unique_active_price(self):
        """Checks if there is more than one active price preventing errors"""
        for record in self:
            if record.active:
                existing_active_price = self.search([
                    ('active', '=', True),
                    ('product_id', '=', record.product_id.id),
                    ('id', '!=', record.id)
                ])
                if existing_active_price:
                    raise ValidationError(
                        "There is already an active price for " +
                        '{record.product_id.name}'
                    )

    @api.constrains('date_ends', 'date_starts', 'product_id')
    def _validate_dates_insert(self):
        """Checks if end date is before start date"""
        for record in self:
            if record.date_ends and record.date_starts:
                if record.date_ends < record.date_starts:
                    raise ValidationError(
                        "Ending Date cannot be before Beginning Date. Check it."
                    )


class Stock(models.Model):
    """Stock entity with the sum of all lots of its referenced product"""
    _name = 'shopping_mall.stock'
    _description = 'Stock amount of sum of all lots belonging to referenced product'

    product_id = fields.Many2one(
        'shopping_mall.product', string='Product', required=True)
    lots_ids = fields.One2many(
        'shopping_mall.lot', 'stock_id', string='Lots')
    sum_of_lots = fields.Integer(
        'Total Stock', compute='_compute_sum_of_lots', store=True)

    @api.depends('lots_ids', 'lots_ids.amount')
    def _compute_sum_of_lots(self):
        for record in self:
            record.sum_of_lots = sum(lot.amount for lot in record.lots_ids)

    def substract_stock(self, amount):
        """Substract cart's line quantity from stock lots"""
        for record in self:
            remaining_amount = amount
            for lot in record.lots_ids:
                if remaining_amount < 0:
                    break

                if lot.amount >= remaining_amount:
                    lot.amount -= remaining_amount
                    remaining_amount = 0

                else:
                    remaining_amount -= lot.amount
                    lot.amount = 0

    def check_available_stock(self, amount):
        """Checks if exist enough amount for buy in a product"""
        for record in self:
            available_stock = 0
            for lot in record.lots_ids:
                available_stock += lot.amount

            if available_stock < amount:
                raise ValidationError(
                    "Not enough stock for" + '{record.product_id.name}')
        return True


class Lot(models.Model):
    """Lot entity with lot number, amount of its referenced product, and expiration date"""
    _name = 'shopping_mall.lot'
    _description = 'Lot individual stock for caducity verification'

    stock_id = fields.Many2one('shopping_mall.stock', string='Stock')
    lot_number = fields.Char('Lot Number')
    amount = fields.Integer('Amount')
    expiration = fields.Date('Expiration Date')
    product_id = fields.Many2one(
        'shopping_mall.product', string='Product', related='stock_id.product_id', store=True)


class Product(models.Model):
    """Product entity with internal id, name, description, and price and stock references"""
    _name = 'shopping_mall.product'
    _description = 'Product base entity'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    stock_id = fields.One2many(
        'shopping_mall.stock', 'product_id', string='Stock')
    stock_amount = fields.Integer(
        string="Total Stock", compute="_compute_stock_amount", store=True)
    lot_ids = fields.One2many(
        'shopping_mall.lot', 'product_id', string='Lot')
    price_ids = fields.One2many(
        'shopping_mall.price', 'product_id', string='Prices')
    active_price = fields.Float(
        String="Active Price", compute="_compute_active_price", store=True)
    cart_products_ids = fields.One2many(
        'shopping_mall.cart_product', 'product_id', string='Cart Product')
    tax = fields.Selection(
        [('0', '0%'), ('5', '5%'), ('10', '10%'), ('21', '21%')], string='IVA', default=0)

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            existing_products = self.search(
                [('name', '=', record.name), ('id', "!=", record.id)])
            if existing_products:
                raise ValidationError(
                    "The name " + '{record.name}' +
                    " is already in use. Choose another name"

                )

    @api.depends('stock_id.sum_of_lots', 'stock_id.lots_ids')
    def _compute_stock_amount(self):
        for product in self:
            total_amount = product.stock_id.sum_of_lots
            product.stock_amount = total_amount

    @api.depends('price_ids.active', 'price_ids.price')
    def _compute_active_price(self):
        for product in self:
            active_prices = product.price_ids.filtered(lambda p: p.active)
            product.active_price = active_prices[0].price if active_prices else 0.0


class CartProducts(models.Model):
    """CartProduct Link for each product and amount of these on a cart"""
    _name = 'shopping_mall.cart_product'
    _description = 'Cart Product'

    cart_id = fields.Many2one('shopping_mall.cart', string='Cart')
    product_id = fields.Many2one('shopping_mall.product', string='Product')
    quantity = fields.Integer('Quantity', default=1)
    base_price = fields.Float('Unitary Price', compute='_compute_base_price')
    line_amount = fields.Float('Line Amount', compute="_compute_line_amount")
    tax_percent = fields.Float(
        'Tax Percent', compute='_compute_tax_percent', store=True)

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 1:
                raise ValidationError("Quantity must be at least 1")

    @api.depends('quantity', 'base_price', 'tax_percent')
    def _compute_line_amount(self):
        """Calculates the total amount with taxes included"""
        for record in self:
            base_amount = record.calculate_base_amount()
            tax_amount = record.calculate_taxes()
            record.line_amount = base_amount + tax_amount

    @api.depends('product_id.active_price')
    def _compute_base_price(self):
        for record in self:
            record.base_price = record.product_id.active_price

    @api.depends('product_id.tax')
    def _compute_tax_percent(self):
        for record in self:
            record.tax_percent = record.product_id.tax

    def calculate_base_amount(self):
        """Calculates base amount, without taxes"""
        return self.quantity * self.base_price

    def calculate_taxes(self):
        """Calculates tax amount)"""
        base_amount = self.calculate_base_amount()
        return base_amount * (self.tax_percent / 100)

    def substract_purchased_stock(self):
        """Calls substracts function in every cart_line"""
        for record in self:
            record.product_id.stock_id.substract_stock(record.quantity)


class Cart(models.Model):
    """Cart entity with each cartProduct and payment relevance information"""
    _name = 'shopping_mall.cart'
    _description = 'Shopping Cart'

    customer_id = fields.Many2one('shopping_mall.customer', string='Customer')
    cart_products_ids = fields.One2many(
        'shopping_mall.cart_product', 'cart_id', string='Cart Products')
    amount = fields.Float('Amount', compute='_compute_amount', store=True)

    discounts = fields.Integer('Discount', default=0)

    discounts_amount = fields.Float(
        'Discounts', compute='_compute_discounts_amount', store=True)
    taxes = fields.Float('Taxes', default=0,
                         compute='_compute_taxes', store=True)
    total_amount = fields.Float(
        'Total Amount', compute='_compute_total_amount', store=True)

    creation_timestamp = fields.Datetime(
        'Creation Timestamp', default=lambda self: fields.Datetime.now())
    payment_method = fields.Selection([
        ('credit_card', 'Credit Card'), ('credit_line', 'Credit Line')
    ], string='Payment Method')

    @api.depends('cart_products_ids.line_amount')
    def _compute_amount(self):
        for record in self:
            record.amount = sum(
                cart_product.line_amount for cart_product in record.cart_products_ids)

    @api.depends('amount', 'taxes', 'discounts')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.amount + record.taxes - record.discounts_amount

    @api.depends('cart_products_ids.line_amount')
    def _compute_taxes(self):
        for record in self:
            record.taxes = sum(cart_product.calculate_taxes()
                               for cart_product in record.cart_products_ids)

    @api.depends('cart_products_ids.line_amount', 'discounts')
    def _compute_discounts_amount(self):
        for record in self:
            record.discounts_amount = (record.amount * record.discounts) / 100

    @api.constrains('total_amount')
    def check_customer_balance(self):
        """Validates if the customer has enough account balance"""
        have_balance = self.customer_id.available_balance >= self.total_amount
        if self.payment_method == 'credit_line' and not have_balance:
            raise ValidationError(
                "No available account balance. Please use another payment method")
        return True

    @api.constrains('cart_products_ids')
    def check_stock_available(self):
        """Checks if is enought stock available for every cart line"""
        for record in self:
            for cart_line in record.cart_products_ids:
                cart_line.product_id.stock_id.check_available_stock(
                    cart_line.quantity)

    def update_customer_balance(self):
        """Update the customer money_spent reducing available balance"""
        self.customer_id.money_spent += self.total_amount

    def update_products_stock(self):
        """Substract purchased products from stock's lots"""
        for cart_line in self.cart_products_ids:
            cart_line.substract_purchased_stock()

    @api.model
    def create(self, vals):
        """Update customer.money_spent when creating a validated cart"""
        cart = super(Cart, self).create(vals)
        cart.update_products_stock()
        if cart.payment_method == "credit_line":
            cart.update_customer_balance()
        return cart


class Customer(models .Model):
    """Customer entity with general data"""
    _name = 'shopping_mall.customer'
    _description = 'Customer'

    external_uid = fields.Char('External UID')
    name = fields.Char('Name')
    surname = fields.Char('Surname')
    birth_date = fields.Date('Date of Birth')
    email = fields.Char('Email')
    dir_line_1 = fields.Char('Address Line 1')
    dir_line_2 = fields.Char('Address Line 2')
    post_code = fields.Char('Postal Code')
    country_id = fields.Many2one('res.country', string='Country')
    guardian_external_uid = fields.Char('Guardian External UID')
    credit_limit_amount = fields.Integer('Credit limit amount', default=2000)
    money_spent = fields.Float('Money Spent')
    available_balance = fields.Float(
        'Available Balance', compute='_compute_available_balance', store=True)
    carts_ids = fields.One2many(
        'shopping_mall.cart', 'customer_id', string='Carts')
    is_adult = fields.Boolean(
        'Is Adult', compute='_compute_is_adult', store=True)

    def obtain_country(self):
        """Verifies if there is an associated country for a customer"""
        for customer in self:
            if customer.country_id:
                return customer.country_id.name
            else:
                return 'No country associated'

    @ api.depends('birth_date')
    def _compute_is_adult(self):
        """Verifies if the customer is an adult (18 years or more)"""
        for customer in self:
            if customer.birth_date:
                today = fields.Date.today()
                age = self.calculate_age(customer.birth_date, today)
                customer.is_adult = age >= 18
            else:
                customer.is_adult = False

    def calculate_age(self, birth_date, today_date):
        """Calculates age based on a birthdate and the current date"""
        if not birth_date:
            return 0
        if isinstance(birth_date, str):
            birth_date = fields.Date.from_string(birth_date)
        if not isinstance(birth_date, date) or not isinstance(today_date, date):
            return 0
        age = today_date.year - birth_date.year
        if (today_date.month, today_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @ api.constrains('is_adult', 'guardian_external_uid')
    def _check_guardian_external_uid(self):
        """Checks if a guardian's external UID is provided for a minor customer"""
        for record in self:
            if record.is_adult is False and not record.guardian_external_uid:
                error_message_main = "Customer {record.name, record.surname} is a minor."
                error_message_sub = "You must provide the NIF of their guardian"
                raise ValidationError(
                    {error_message_main, error_message_sub}
                )

    @api.depends('money_spent', 'credit_limit_amount')
    def _compute_available_balance(self):
        for record in self:
            record.available_balance = record.credit_limit_amount - record.money_spent
