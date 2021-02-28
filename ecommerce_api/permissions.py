import graphene
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import re
from django.db.models import Q


def is_authenticated(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise Exception("You are not authorized to perform operations")

        return func(cls, info, **kwargs)

    return wrapper


def paginate(model_type):

    structure = {
        "total": graphene.Int(),
        "size": graphene.Int(),
        "current": graphene.Int(),
        "has_next": graphene.Boolean(),
        "has_prev": graphene.Boolean(),
        "results": graphene.List(model_type)
    }

    return type(f"{model_type}Paginated", (graphene.ObjectType,), structure)


def resolve_paginated(query_data, info, page_info):
    def get_paginated_data(qs, paginated_type, page):
        page_size = settings.GRAPHENE.get("PAGE_SIZE", 10)

        try:
            qs.count()
        except:
            raise Exception(qs)

        p = Paginator(qs, page_size)

        try:
            page_obj = p.page(page)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)

        result = paginated_type.graphene_type(
            total=p.num_pages,
            size=qs.count(),
            current=page_obj.number,
            has_next=page_obj.has_next(),
            has_prev=page_obj.has_previous(),
            results=page_obj.object_list
        )

        return result

    return get_paginated_data(query_data, info.return_type, page_info)
