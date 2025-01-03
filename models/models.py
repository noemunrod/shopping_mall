# -*- coding: utf-8 -*-
"""Odoo module for Shopping Mall activities"""
from odoo import _, api, fields, models  # type: ignore


class Price(models.Model):
    """Price entity with status and timestamps of activation"""
    _name = 'price.name'
    _description = 'Collection of prices, activated and not'
    id = fields.Integer('price_id')
    date_starts = fields.Datetime('price_date_starts')
    date_ends = fields.Datetime('price_date_ends')
    active = fields.Boolean('price_active')


class Stock(models.Model):
    """Stock entity with the sum of all lots of his referenced product"""
    _name = 'stock.name'
    _description = 'Stock amount of sum of all lots belonging referenced product'
    sum_of_lots = fields.Integer('sum_of_lots')


class Lot(models.Model):
    """Lot entity with lot number, amount of his referenced product and expiration date"""
    _name = 'lot'
    _description = 'Lot individual stock for caducity verification'
    number = fields.Integer('id')
    expiration = fields.Date('expiration')
    amount = fields.Integer('stock')


class Product(models.Model):
    """Product entity with internal id, name, description, and price and stock references"""
    _name = 'product'
    _description = 'Product base entity'
    id = fields.Integer('id')
    name = fields.Char('name')
    description = fields.Char('description')


class CartProducts(models.Model):
    """CartProduct Link for each product and amount of these on a cart"""
    _name = 'cart_products'
    _description = 'cart_products'
    quantity = fields.Integer('quantity')


class Cart(models.Model):
    """Cart entity with each cartProduct and payment relevance information"""
    _name = 'cart'
    _description = 'cart'
    amount = fields.Float('amount')
    discounts = fields.Float('discounts')
    total_amount = fields.Float('total_amount')
    taxes = fields.Float('taxes')
    creation_timestamp = fields.Datetime('creation_timestamp')


class Customer(models.Model):
    """Customer entity with general data"""
    _name = 'customer'
    _description = 'customer'
    id = fields.Integer('id')
    external_uid = fields.Char('external_uid')
    name = fields.Char('name')
    surname = fields.Char('surname')
    email = fields.Char('email')
    dir_line_1 = fields.Char('dir_line_1')
    dir_line_2 = fields.Char('dir_line_2')
    post_code = fields.Integer('post_code')
