# -*- coding: utf-8 -*-
"""Odoo module for Shopping shopping activities"""
from datetime import datetime
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

    price = fields.Float('price')
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
                        f"There is already an active price for '{record.product_id.name}'"
                    )

    @api.constrains('date_ends', 'date_starts', 'product_id')
    def _validate_dates_insert(self):
        """Checks if end date is before start date"""
        for record in self:
            if record.date_ends < record.date_starts:
                raise ValidationError(
                    "Ending Date cannot be before Beginning Date. Please use correct time intervals"
                )


class Stock(models.Model):
    """Stock entity with the sum of all lots of its referenced product"""
    _name = 'shopping_mall.stock'
    _description = 'Stock amount of sum of all lots belonging to referenced product'

    product_id = fields.Many2one('shopping_mall.product', string='Product')
    lots_ids = fields.One2many(
        'shopping_mall.lot', 'stock_id', string='lots')
    sum_of_lots = fields.Integer(
        'Total Stock', compute='_compute_sum_of_lots', store=True)

    @api.depends('lots_ids')
    def _compute_sum_of_lots(self):
        for record in self:
            record.sum_of_lots = sum(lot.amount for lot in record.lots_ids)


class Lot(models.Model):
    """Lot entity with lot number, amount of its referenced product, and expiration date"""
    _name = 'shopping_mall.lot'
    _description = 'Lot individual stock for caducity verification'

    number = fields.Integer('number')
    stock_id = fields.Many2one('shopping_mall.stock', string='stock')
    product_id = fields.Many2one('shopping_mall.product', string='Product')
    lot_number = fields.Char('Lot Number')
    expiration = fields.Date('Expiration Date')
    amount = fields.Integer('amount')


class Product(models.Model):
    """Product entity with internal id, name, description, and price and stock references"""
    _name = 'shopping_mall.product'
    _description = 'Product base entity'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    price_ids = fields.One2many(
        'shopping_mall.price', 'product_id', string='Prices')
    stock_id = fields.Many2one(
        'shopping_mall.stock', string='Stock')
    lot_ids = fields.One2many(
        'shopping_mall.lot', 'product_id', string='Lot')
    cart_products_ids = fields.One2many(
        'shopping_mall.cart_product', 'product_id', string='Cart Product')

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            existing_products = self.search(
                [('name', '=', record.name), ('id', "!=", record.id)])
            if existing_products:
                raise ValidationError(
                    f"The name '{record.name}' is already in use. Please choose another name."
                )


class CartProducts(models.Model):
    """CartProduct Link for each product and amount of these on a cart"""
    _name = 'shopping_mall.cart_product'
    _description = 'Cart Product'

    cart_id = fields.Many2one('shopping_mall.cart', string='Cart')
    product_id = fields.Many2one('shopping_mall.product', string='Product')
    quantity = fields.Integer('quantity')


class Cart(models.Model):
    """Cart entity with each cartProduct and payment relevance information"""
    _name = 'shopping_mall.cart'
    _description = 'Shopping Cart'

    customer_id = fields.Many2one('shopping_mall.customer', string='Customer')
    cart_product_ids = fields.One2many(
        'shopping_mall.cart_product', 'cart_id', string='Products')
    amount = fields.Float('Amount')
    discounts = fields.Float('Discounts')
    total_amount = fields.Float('Total Amount')
    taxes = fields.Float('Taxes')
    creation_timestamp = fields.Datetime(
        'Creation Timestamp', default=fields.Datetime.now())


class Customer(models.Model):
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
    guardian_external_uid = fields.Char('guardian_external_uid')
    credit_limit_amount = fields.Integer('credit_limit_amount')
    money_spent = fields.Float('money_spent')
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

    @api.depends('birth_date')
    def _compute_is_adult(self):
        """Verifies if the customer is an adult (18 years or more)"""
        for customer in self:
            today = datetime.today()
            age = self.calculate_age(customer.birth_date, today)
            if age >= 18:
                customer.is_adult = True
            else:
                customer.is_adult = False

    @staticmethod
    def calculate_age(birth_date, today_date):
        """Calculates age based on a birthdate and the current date"""
        age = today_date.year - birth_date.year
        if not birth_date:
            return 0
        if (today_date.month, today_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @api.constrains('is_adult', 'guardian_external_uid')
    def _check_guardian_external_uid(self):
        """Checks if a guardian's external UID is provided for a minor customer"""
        for customer in self:
            if not customer.is_adult and not customer.guardian_external_uid:
                raise ValidationError(
                    f"Customer {customer.name} {customer.surname} is a minor."
                    f"You must provide the NIF of their guardian"
                )
