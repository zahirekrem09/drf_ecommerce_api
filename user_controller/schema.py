import graphene
from .models import CustomUser, ImageUpload
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate
from ecommerce_api.authentication import TokenManager
from datetime import datetime
from ecommerce_api.permissions import is_authenticated, paginate
from django.conf import settings
from graphene_file_upload.scalars import Upload


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser


class ImageUploadType(DjangoObjectType):
    image = graphene.String()

    class Meta:
        model = ImageUpload

    def resolve_image(self, info):
        if self.image:
            return "{}{}{}".format(settings.S3_BUCKET_URL, settings.MEDIA_URL, self.image)
        return None


class RegisterUser(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    def mutate(self, info, email, password, **kwargs):
        user = CustomUser.objects.create_user(email, password, **kwargs)

        return RegisterUser(
            status=True,
            message="User created successfully",
            user=user,

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
            raise Exception("invalid credentials email or password is wrong")

        user.last_login = datetime.now()
        user.save()

        access = TokenManager.get_access({"user_id": user.id})
        refresh = TokenManager.get_refresh({"user_id": user.id})

        return LoginUser(
            access=access,
            refresh=refresh,
            user=user
        )


class GetAccess(graphene.Mutation):
    access = graphene.String()

    class Arguments:
        refresh = graphene.String(required=True)

    def mutate(self, info, refresh):
        token = TokenManager.decode_token(refresh)

        if not token or token["type"] != "refresh":
            raise Exception("Invalid token or has expired")

        access = TokenManager.get_access({"user_id": token["user_id"]})

        return GetAccess(
            access=access
        )


class ImageUploadMain(graphene.Mutation):
    image = graphene.Field(ImageUploadType)

    class Arguments:
        image = Upload(required=True)

    def mutate(self, info, image):
        image = ImageUpload.objects.create(image=image)

        return ImageUploadMain(
            image=image
        )


class Query(graphene.ObjectType):
    users = graphene.Field(paginate(UserType),  page=graphene.Int())
    image_uploads = graphene.Field(
        paginate(ImageUploadType), page=graphene.Int())

    # @is_authenticated
    def resolve_users(self, info, **kwargs):
        # print(info.context.user)
        return CustomUser.objects.filter(**kwargs)

    def resolve_image_uploads(self, info, **kwargs):
        return ImageUpload.objects.filter(**kwargs)


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()
    get_access = GetAccess.Field()
    image_upload = ImageUploadMain.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
