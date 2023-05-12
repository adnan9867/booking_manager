from django.urls import path

from booking.views import EmailTypesViewSet
from .views import *

urlpatterns = [
    path("user_login", UserLoginViewSet.as_view({"post": "create"}), name="user_login"),
    path(
        "mobile_login",
        MobileLoginViewSet.as_view({"post": "create"}),
        name="user_login",
    ),
    path(
        "user_email_signup",
        UserEmailSignupViewSet.as_view({"post": "create"}),
        name="user_email_signup",
    ),
    path(
        "user_information_signup",
        UserAccountInformationView.as_view({"post": "create"}),
        name="user_information_signup",
    ),
    path(
        "customer_signup",
        CustomerSignUpView.as_view({"post": "create"}),
        name="user_information_signup",
    ),
    path(
        "update_profile",
        UpdateUserProfile.as_view({"put": "update"}),
        name="create_location",
    ),


    path(
        "user_card_list",
        UserPaymentMethod.as_view({"get": "list"}),
        name="user_card_list",
    ),
    path(
        "delete_user_card",
        UserPaymentMethod.as_view({"delete": "destroy"}),
        name="user_card_list",
    ),
    path(
        "admin_card_list",
        AdminCardDetailViewSet.as_view({"get": "list"}),
        name="user_card_list",
    ),
    path(
        "add_user_card",
        UserPaymentMethod.as_view({"post": "create"}),
        name="user_card_list",
    ),

    #   Forget Password

    path(
        "forget_password",
        ForgetPassword.as_view({"post": "create"}),
        name="user_card_list",
    ),
    path(
        "reset_password",
        ResetPassword.as_view({"post": "create"}),
        name="user_card_list",
    ),

    path(
        "import_customers",
        ImportCustomerCsv.as_view({"post": "create"}),
        name="user_card_list",
    ),

    path(
        "update_cleaner_location",
        CleanerLocationView.as_view({"post": "create"}),
        name="user_card_list",
    ),
    path(
        "create_review",
        UserReviewSystem.as_view({"post": "create"}),
        name="customer_review",
    ),
    path(
        "customer_reviews_list",
        UserReviewSystem.as_view({"get": "customer_reviews"}),
        name="user_card_list",
    ),
    path(
        "update_reviews",
        UserReviewSystem.as_view({"put": "update"}),
        name="user_card_list",
    ),
    path(
        "update_profile_picture",
        UpdateUserProfilePicture.as_view({"put": "update"}),
        name="update_profile_picture",
    ),
]
