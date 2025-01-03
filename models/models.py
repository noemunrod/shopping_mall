# -*- coding: utf-8 -*-
from odoo import _, api, fields, models  # type: ignore


class price(models.Model):
    _name = 'price.name'
    _description = 'Collection of prices, activated and not'
    id = fields.Integer('price_id')
    date_starts = fields.Datetime('price_date_starts')
    date_ends = fields.Datetime('price_date_ends')
    active = fields.Boolean('price_active')


class stock(models.Model):
    _name = 'stock.name'
    _description = 'Stock amount of sum of all lots belonging referenced product'
    sum_of_lots = fields.Integer('sum_of_lots')


class lot(models.Model):
    _name = 'lot'
    _description = 'Lot individual stock for caducity verification'
    id = fields.Integer('id')
    expiration = fields.Date('expiration')
    amount = fields.Integer('stock')


class product(models.Model):
    _name = 'product'
    _description = 'Product base entity'
    id = fields.Integer('id')
    name = fields.Char('name')
    description = fields.Char('description')


class cart_products(models.Model):
    _name = 'cart_products'
    _description = 'cart_products'
    quantity = fields.Integer('quantity')


class cart(models.Model):
    _name = 'cart'
    _description = 'cart'
    amount = fields.Float('amount')
    discounts = fields.Float('discounts')
    total_amount = fields.Float('total_amount')
    taxes = fields.Float('taxes')
    creation_timestamp = fields.Datetime('creation_timestamp')


class customer(models.Model):
    _name = 'customer'
    _description = 'customer'
