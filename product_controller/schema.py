import graphene
from graphene_django import DjangoObjectType
from ecommerce_api.permissions import paginate, is_authenticated, get_query
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


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType, name=graphene.String())
    products = graphene.Field(paginate(ProductType), search=graphene.String(),
                              min_price=graphene.Float(), max_price=graphene.Float(), category=graphene.String(),
                              business=graphene.String(), sort_by=graphene.String(), is_asc=graphene.Boolean(), mine=graphene.Boolean())

    def resolve_categories(self, info, name=False):
        query = Category.objects.prefetch_related("product_categories")

        if name:
            query = query.filter(Q(name__icontains=name) |
                                 Q(name__iexact=name)).distinct()

        return query

    def resolve_products(self, info, **kwargs):
        # mine = kwargs.get("mine", False)
        # if mine and not info.context.user:
        #     raise Exception("User auth required")
        query = Product.objects.select_related("category", "business").prefetch_related(
            "product_images", "product_comments", "products_wished", "product_carts", "product_requests"
        )
        if kwargs.get("search", None):
            qs = kwargs["search"]
            search_fields = (
                "name", "description", "category__name"
            )

            search_data = get_query(qs, search_fields)
            query = query.filter(search_data)

        if kwargs.get("min_price", None):
            qs = kwargs["min_price"]

            query = query.filter(Q(price__gt=qs) | Q(price=qs)).distinct()

        if kwargs.get("max_price", None):
            qs = kwargs["max_price"]

            query = query.filter(Q(price__lt=qs) | Q(price=qs)).distinct()

        if kwargs.get("category", None):
            qs = kwargs["category"]

            query = query.filter(Q(category__name__icontains=qs)
                                 | Q(category__name__iexact=qs)).distinct()

        if kwargs.get("business", None):
            qs = kwargs["business"]

            query = query.filter(Q(business__name__icontains=qs)
                                 | Q(business__name__iexact=qs)).distinct()

        if kwargs.get("sort_by", None):
            qs = kwargs["sort_by"]
            is_asc = kwargs.get("is_asc", False)
            if not is_asc:
                qs = f"-{qs}"
            query = query.order_by(qs)

        return query
