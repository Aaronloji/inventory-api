from marshmallow import Schema, fields, validate

from app.models import MovementType, Role

# ---------- Auth ----------


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    role = fields.Str(validate=validate.OneOf(Role.ALL), load_default=Role.VIEWER)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class UserUpdateSchema(Schema):
    role = fields.Str(validate=validate.OneOf(Role.ALL))
    is_active = fields.Bool()


# ---------- Categorías ----------


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=80))
    description = fields.Str(allow_none=True)


# ---------- Productos ----------


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str(required=True, validate=validate.Length(min=2, max=40))
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    description = fields.Str(allow_none=True)
    unit_price = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0))
    min_stock = fields.Int(load_default=0, validate=validate.Range(min=0))
    category_id = fields.Int(required=True)
    stock = fields.Int(dump_only=True)
    low_stock = fields.Bool(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    category = fields.Nested(CategorySchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=120))
    description = fields.Str(allow_none=True)
    unit_price = fields.Decimal(as_string=True, validate=validate.Range(min=0))
    min_stock = fields.Int(validate=validate.Range(min=0))
    category_id = fields.Int()
    is_active = fields.Bool()


class ProductQuerySchema(Schema):
    q = fields.Str(load_default=None)
    category_id = fields.Int(load_default=None)
    low_stock = fields.Bool(load_default=None)
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


class PaginatedProductSchema(Schema):
    items = fields.List(fields.Nested(ProductSchema))
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    pages = fields.Int()


# ---------- Movimientos ----------


class UserBriefSchema(Schema):
    id = fields.Int()
    username = fields.Str()


class ProductBriefSchema(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()


class MovementSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(MovementType.ALL))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    note = fields.Str(allow_none=True)
    stock_after = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserBriefSchema, dump_only=True)
    product = fields.Nested(ProductBriefSchema, dump_only=True)


class MovementQuerySchema(Schema):
    product_id = fields.Int(load_default=None)
    type = fields.Str(load_default=None, validate=validate.OneOf(MovementType.ALL))
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


class PaginatedMovementSchema(Schema):
    items = fields.List(fields.Nested(MovementSchema))
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    pages = fields.Int()


# ---------- Reportes ----------


class StatsSchema(Schema):
    total_products = fields.Int()
    total_categories = fields.Int()
    low_stock_count = fields.Int()
    inventory_value = fields.Decimal(as_string=True)
    movements_last_7_days = fields.Int()
