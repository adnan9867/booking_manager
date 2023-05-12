from django.urls import path
from .views import *

urlpatterns = [
    path(
        "create_cleaner", CleanerViewSet.as_view({"post": "create"}), name="user_login"
    ),
    path("cleaner_list", CleanerViewSet.as_view({"get": "list"}), name="user_login"),
    path(
        "update_cleaner",
        CleanerViewSet.as_view({"put": "update"}),
        name="update_cleaner",
    ),
    # Customer
    path(
        "create_customer",
        CustomerViewSet.as_view({"post": "create"}),
        name="user_login",
    ),
    path("customer_list", CustomerViewSet.as_view({"get": "list"}), name="user_login"),
    path(
        "update_customer",
        CustomerViewSet.as_view({"put": "update"}),
        name="update_cleaner",
    ),
    # print out wowels in string



    # Cleaner LeaveTime
    path(
        "create_leave",
        ClearnerLeaveTimeViewSet.as_view({"post": "create"}),
        name="create_leave",
    ),
    path(
        "list_leaves",
        ClearnerLeaveTimeViewSet.as_view({"get": "list"}),
        name="list_leaves",
    ),
    path(
        "delete_leave/<int:id>",
        ClearnerLeaveTimeViewSet.as_view({"delete": "destroy"}),
        name="delete_leave",
    ),
    # Cleaner Tasks
    path(
        "create_task",
        ManagerTaskViewSet.as_view({"post": "create"}),
        name="create_task",
    ),
    path(
        "list_tasks",
        ManagerTaskViewSet.as_view({"get": "list"}),
        name="list_tasks",
    ),
    path(
        "complete_task",
        ManagerTaskViewSet.as_view({"put": "update"}),
        name="list_tasks",
    ),
    path(
        "update_task",
        ManagerTaskViewSet.as_view({"put": "update_task"}),
        name="list_tasks",
    ),
    path(
        "delete_task/<int:id>",
        ManagerTaskViewSet.as_view({"delete": "destroy"}),
        name="delete_task",
    ),
    path(
        "manager_list_tasks",
        ManagerTaskViewSet.as_view({"get": "manager_task"}),
        name="cleaner_list",
    ),
    # Cleaner Location
    path(
        "cleaner_location",
        ServiceProviderLocationViewSet.as_view({"get": "list"}),
        name="create_location",
    ),


]
