# -*- coding: utf-8 -*-
"""Odoo module for Shopping shopping activities"""
from odoo import api, fields, models  # type: ignore


class Price(models.Model):
    """Price entity with status and timestamps of activation"""
    _name = 'shopping_mall.price'
    _description = 'Collection of prices, activated and not'

    price = fields.Float('price')
    date_starts = fields.Datetime('Start Date')
    date_ends = fields.Datetime('End Date')
    active = fields.Boolean('Active', default=True)
    product_id = fields.Many2one('shopping_mall.product', string='Product')


class Stock(models.Model):
    """Stock entity with the sum of all lots of its referenced product"""
    _name = 'shopping_mall.stock'
    _description = 'Stock amount of sum of all lots belonging to referenced product'

    product_id = fields.Many2one('shopping_mall.product', string='Product')
    lots_ids = fields.One2many(
        'shopping_mall.lot', 'stock_id', string='lots')
    sum_of_lots = fields.Integer(
        'Total Stock', compute='_compute_sum_of_lots,store=True')


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
        'Creation Timestamp', default=fields.Datetime.now)


class Customer(models.Model):
    """Customer entity with general data"""
    _name = 'shopping_mall.customer'
    _description = 'Customer'

    external_uid = fields.Char('External UID')
    name = fields.Char('Name')
    surname = fields.Char('Surname')
    email = fields.Char('Email')
    dir_line_1 = fields.Char('Address Line 1')
    dir_line_2 = fields.Char('Address Line 2')
    post_code = fields.Char('Postal Code')
    carts_ids = fields.One2many(
        'shopping_mall.cart', 'customer_id', string='Carts')
