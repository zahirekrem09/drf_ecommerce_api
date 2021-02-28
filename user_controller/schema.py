import graphene
from .models import CustomUser
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate


class UserType(DjangoObjectType):

    class Meta:
        model = CustomUser


class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()


schema = graphene.Schema(query=Query)
