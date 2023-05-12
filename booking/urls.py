from django.urls import path
from .views import *

urlpatterns = [
    # Company
    path(
        "create_company",
        CompanyViewSet.as_view({"post": "create"}),
        name="create_company",
    ),
    path(
        "update_company",
        CompanyViewSet.as_view({"put": "update"}),
        name="update_company",
    ),
    path("get_company", CompanyViewSet.as_view({"get": "list"}), name="get_company"),
    path("get_latest", GetLatestViewSet.as_view({"get": "list"}), name="get_latest"),

    # Tax
    path("create_tax", TaxViewSet.as_view({"post": "create"}), name="create_tax"),
    path("update_tax", TaxViewSet.as_view({"put": "update"}), name="update_tax"),
    path("get_tax", TaxViewSet.as_view({"get": "list"}), name="get_tax"),
    # Service
    path(
        "create_service",
        ServicesViewSet.as_view({"post": "create"}),
        name="create_service",
    ),
    path(
        "update_service",
        ServicesViewSet.as_view({"put": "update"}),
        name="update_service",
    ),
    path("get_service", ServicesViewSet.as_view({"get": "list"}), name="get_service"),
    path("service_listing", ServicesViewSet.as_view({"get": "active_services"}), name="get_service"),
    path(
        "delete_service/<int:pk>",
        ServicesViewSet.as_view({"delete": "destroy"}),
        name="delete_service",
    ),
    path(
        "update_service_status",
        ServicesViewSet.as_view({"put": "update_status"}),
        name="update_status",
    ),
    path(
        "retrieve_service/<int:service_id>",
        ServicesViewSet.as_view({"get": "retrieve"}),
        name="update_status",
    ),
    # Packages
    path(
        "create_package",
        PackagesViewSet.as_view({"post": "create"}),
        name="create_package",
    ),
    path(
        "update_package",
        PackagesViewSet.as_view({"put": "update"}),
        name="update_package",
    ),
    path(
        "delete_package/<int:pk>",
        PackagesViewSet.as_view({"delete": "destroy"}),
        name="delete_package",
    ),
    # Items
    path(
        "create_item",
        PackageItemsViewSet.as_view({"post": "create"}),
        name="create_item",
    ),
    path(
        "update_item",
        PackageItemsViewSet.as_view({"put": "update"}),
        name="update_item",
    ),
    path(
        "delete_item/<int:pk>",
        PackageItemsViewSet.as_view({"delete": "destroy"}),
        name="delete_item",
    ),
    # Extras
    path(
        "create_extras",
        ServiceExtrasViewSet.as_view({"post": "create"}),
        name="create_extras",
    ),
    path(
        "update_extras",
        ServiceExtrasViewSet.as_view({"put": "update"}),
        name="update_extras",
    ),
    path(
        "delete_extras/<int:pk>",
        ServiceExtrasViewSet.as_view({"delete": "destroy"}),
        name="delete_extras",
    ),
    # Booking
    path(
        "create_booking/<str:service>",
        BookingViewSet.as_view({"post": "create"}),
        name="create_booking",
    ),
    path(
        "user_create_booking/<str:service>",
        UserBookingViewSet.as_view({"post": "create"}),
        name="create_booking",
    ),
    path(
        "admin_create_booking/<str:service>",
        AdminBookingViewSet.as_view({"post": "create"}),
        name="admin_create_booking",
    ),
    path(
        "service_booking/<str:slug>",
        ServiceBookingViewSet.as_view({"get": "retrieve"}),
        name="service_booking",
    ),
    path("booking_list", BookingViewSet.as_view({"get": "list"}), name="booking_list"),
    path("get_booking/<int:pk>", BookingViewSet.as_view({"get": "retrieve"}), name="get_booking"),
    path("booking_by_created", BookingViewSet.as_view({"get": "booking_created_at"}), name="booking_created_at"),
    path(
        "update_booking",
        RescheduleBookingViewSet.as_view({"put": "update"}),
        name="update_booking",
    ),
    path(
        "update_booking_package",
        UpdateBookingService.as_view({"put": "update"}),
        name="update_booking",
    ),
    path(
        "cancel_booking",
        CancelBookingView.as_view({"post": "create"}),
        name="cancel_booking",
    ),
    path(
        "mark_complete",
        MarkBookingCompleteView.as_view({"post": "create"}),
        name="cancel_booking",
    ),
    # Booking Details
    path(
        "booking_details/<int:booking_id>",
        BookingDetailViewSet.as_view({"get": "list"}),
        name="booking_details",
    ),
    # Booking Problems
    path(
        "update_create_problem",
        BookingProblemsViewSet.as_view({"post": "create"}),
        name="update_create_problem",
    ),
    path(
        "get_problem/<int:booking>",
        BookingProblemsViewSet.as_view({"get": "list"}),
        name="get_problem",
    ),
    # Booking Attachments
    path(
        "create_attachment",
        BookingAttachmentsViewSet.as_view({"post": "create"}),
        name="create_attachment",
    ),
    path(
        "get_attachment/<int:booking>",
        BookingAttachmentsViewSet.as_view({"get": "list"}),
        name="get_attachment",
    ),
    path(
        "delete_attachment/<int:pk>",
        BookingAttachmentsViewSet.as_view({"delete": "destroy"}),
        name="delete_attachment",
    ),
    # Booking Dispatch
    path(
        "create_dispatch",
        BookingUpdateViewSet.as_view({"post": "create"}),
        name="create_dispatch",
    ),
    path(
        "booking_dispatch_list",
        BookingUpdateViewSet.as_view({"get": "list"}),
        name="booking_list",
    ),
    path(
        "dispatch_list",
        BookingUpdateViewSet.as_view({"get": "dispatch_list"}),
        name="dispatch_list",
    ),
    path(
        "delete_dispatch/<int:pk>",
        BookingUpdateViewSet.as_view({"delete": "destroy"}),
        name="delete_dispatch",
    ),
    # Admin CHat
    path("admin_chat", AdminChatViewSet.as_view({"post": "create"}), name="admin_chat"),
    path(
        "get_admin_chat",
        AdminChatViewSet.as_view({"get": "list"}),
        name="get_admin_chat",
    ),
    path(
        "get_user_chat", UserChatViewSet.as_view({"get": "list"}), name="get_admin_chat"
    ),
    path(
        "get_cleaner_chat", CleanerChatViewSet.as_view({"get": "list"}), name="get_admin_chat"
    ),
    path(
        "get_booking_chat/<int:pk>", BookingChatViewSet.as_view({"get": "list"}), name="get_admin_chat"
    ),
    path(
        "admin_chat_detail",
        AdminChatDetailViewSet.as_view({"get": "list"}),
        name="get_admin_chat",
    ),
    # Booking Dashboard
    path(
        "booking_dashboard",
        BookingDashboardViewSet.as_view({"get": "list"}),
        name="booking_dashboard",
    ),
    # Charge
    path(
        "charge_booking",
        ChargeViewSet.as_view({"post": "create"}),
        name="booking_dashboard",
    ),
    # Dashboard Data
    path(
        "dashboard_data",
        DashboardAPIsViewSet.as_view({"get": "list"}),
        name="dashboard_data",
    ),
    path(
        "notifications",
        BookingNotificationViewSet.as_view({"get": "list"}),
        name="notifications",
    ),
    path(
        "dispatch_notifications",
        MobileNotificationViewSet.as_view({"get": "list"}),
        name="notifications",
    ),
    # Booking Reports
    path(
        "booking_reports",
        BookingReportsViewSet.as_view({"get": "list"}),
        name="booking_reports",
    ),
    # User Side Booking
    path(
        "user_current_booking",
        UserCurrentBookingView.as_view({"get": "list"}),
        name="user_booking",
    ),
    path(
        "user_booking_listing",
        UserBookingView.as_view({"get": "list"}),
        name="user_booking",
    ),
    # User Admin Booking
    path(
        "admin_user_booking",
        UserAdminBookingView.as_view({"get": "list"}),
        name="user_booking",
    ),
    # Cancel Booking
    path(
        "cleaner_booking_listing",
        CleanerBookingView.as_view({"get": "list"}),
        name="user_booking",
    ),
    # Payroll
    path("payroll", PayrollViewSet.as_view({"get": "list"}), name="payroll"),
    path("payroll_csv", PayrollCsvViewSet.as_view({"get": "list"}), name="payroll"),
    path("customer_csv", CustomerCsvViewSet.as_view({"get": "list"}), name="payroll"),
    path("invoices", InvoiceViewSet.as_view({"get": "list"}), name="invoices"),
    # Old Dispatcher
    path(
        "get_resources", DispatcherResources.as_view({"get": "list"}), name="dispatcher"
    ),
    path("get_events", DispatcherEvents.as_view({"get": "list"}), name="get_events"),
    path(
        "new_dispatcher_ajax",
        NewDispatcher.as_view({"post": "create"}),
        name="get_events",
    ),
    path(
        "update_dispatcher_ajax",
        UpdateDispatcher.as_view({"put": "update"}),
        name="get_events",
    ),
    path(
        "remove_dispatcher",
        RemoveDispatcher.as_view({"delete": "destroy"}),
        name="get_events",
    ),
    # User Card Details
    path(
        "user_card_details",
        UserCardDetails.as_view({"get": "list"}),
        name="user_card_details",
    ),

    # Charge Tip
    path(
        "charge_tip",
        ChargeTipViewSet.as_view({"post": "create"}),
        name="charge_tip",
    ),

    # Email Types
   path(
        "create_email_type",
        EmailTypesViewSet.as_view({"post": "create"}),
        name="user_card_list",
    ),
    path(
        "list_email_type",
        EmailTypesViewSet.as_view({"post": "create"}),
        name="user_card_list",
    ),
    path(
        "update_email_type",
        EmailTypesViewSet.as_view({"put": "update"}),
        name="user_card_list",
    ),

    # Email Logs
    path(
        "list_email_logs",
        EmailLogsViewSet.as_view({"get": "list"}),
        name="user_card_list",
    ),
    # Customer
    path(
        "get_customer",
        RetrieveCustomer.as_view({"get": "retrieve"}),
        name="customer_list",
    ),

    path(
        "get_email_types",
        EmailTypesViewSet.as_view({"get": "list"}),
        name="customer_list",
    ),

    path(
        "get_managers",
        ManagerViewSet.as_view({"get": "list"}),
        name="customer_list",
    ),

    # Payment
    path(
        "get_payment",
        PaymentSaleView.as_view({"get": "list"}),
        name="customer_list",
    ),

    # Payroll Ledger
    path(
        "get_payroll_ledger",
        PayrollLedgerViewSet.as_view({"get": "list"}),
        name="customer_list",
    ),
    path(
        "create_payroll_ledger",
        PayrollLedgerViewSet.as_view({"post": "create"}),
        name="customer_list",
    ),

    path(
        "banner_listing",
        BannerViewSet.as_view({"get": "list"}),
        name="customer_list",
    ),
]
