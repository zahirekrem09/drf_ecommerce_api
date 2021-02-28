import graphene
from .models import CustomUser
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate
from ecommerce_api.authentication import TokenManager
from datetime import datetime


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser


class RegisterUser(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    # user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    def mutate(self, info, email, password, **kwargs):
        user = CustomUser.objects.create_user(email, password, **kwargs)

        return RegisterUser(
            status=True,
            message="User created successfully"
            # user=user,

        )


class LoginUser(graphene.Mutation):
    access = graphene.String()
    refresh = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = authenticate(username=email, password=password)

        if not user:
            raise Exception("invalid credentials")

        user.last_login = datetime.now()
        user.save()

        access = TokenManager.get_access({"user_id": user.id})
        refresh = TokenManager.get_refresh({"user_id": user.id})

        return LoginUser(
            access=access,
            refresh=refresh,
            user=user
        )


class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
