from django.contrib import admin
from django.contrib.auth import get_user_model

from orders_app.models import Order

User = get_user_model()


class BusinessUserFilter(admin.SimpleListFilter):
    title = "Business User"
    parameter_name = "business_user"

    def lookups(self, request, model_admin):
        business_users = User.objects.filter(type="business").values_list("username", "username").distinct()
        return business_users

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(business_user__username=self.value(), business_user__type="business")
        return queryset


class CustomerUserFilter(admin.SimpleListFilter):
    title = "Customer User"
    parameter_name = "customer_user"

    def lookups(self, request, model_admin):
        customer_users = User.objects.filter(type="customer").values_list("username", "username").distinct()
        return customer_users

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(customer_user__username=self.value(), customer_user__type="customer")
        return queryset


class OrderAdmin(admin.ModelAdmin):
    """
    Custom form for Order model to handle user-related fields.
    """

    list_display = ("offer_detail", "id", "business_user", "customer_user", "status", "created_at", "updated_at")
    search_fields = ("offer_detail__title",)
    list_filter = ("status", "created_at", BusinessUserFilter, CustomerUserFilter)
    fields = ("offer_detail", "id", "business_user", "customer_user", "status", "created_at", "updated_at")
    readonly_fields = (
        "offer_detail",
        "id",
        "business_user",
        "customer_user",
        "created_at",
        "updated_at",
    )


admin.site.register(Order, OrderAdmin)
