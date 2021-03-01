import graphene
from graphene_django import DjangoObjectType
from ecommerce_api.permissions import paginate, is_authenticated
from django.db.models import Q

from .models import (
    Category, Business, Product, ProductComment,
    ProductImage, Wish, Cart, RequestCart
)


class CategoryType(DjangoObjectType):
    count = graphene.Int()

    class Meta:
        model = Category

    def resolve_count(self, info):
        return self.product_categories.count()


class BusinessType(DjangoObjectType):

    class Meta:
        model = Business


class ProductType(DjangoObjectType):

    class Meta:
        model = Product


class ProductCommentType(DjangoObjectType):

    class Meta:
        model = ProductComment


class ProductImageType(DjangoObjectType):

    class Meta:
        model = ProductImage


class WishType(DjangoObjectType):

    class Meta:
        model = Wish


class CartType(DjangoObjectType):

    class Meta:
        model = Cart


class RequestCartType(DjangoObjectType):

    class Meta:
        model = RequestCart
