from django.contrib import admin
from django.contrib.auth import get_user_model

from offers_app.models import Offer, OfferDetail

User = get_user_model()


class BusinessUserFilter(admin.SimpleListFilter):
    title = "Business User"
    parameter_name = "business_user"

    def lookups(self, request, model_admin):
        business_users = User.objects.filter(type="business").values_list("username", "username").distinct()
        return business_users

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__username=self.value(), user__type="business")
        return queryset


class OfferAdminForm(admin.ModelAdmin):
    """
    Custom form for Offer model to handle user-related fields.
    """

    list_display = ("title", "id", "user", "created_at", "updated_at")
    search_fields = ("title", "user__username", "user__email")
    list_filter = (BusinessUserFilter, "created_at")
    fields = ("title", "id", "user", "image", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "user", "id")


class BusinessUserOfferFilter(admin.SimpleListFilter):
    title = "Business User (Offer)"
    parameter_name = "business_user_offer"

    def lookups(self, request, model_admin):
        business_users = User.objects.filter(type="business").values_list("username", "username").distinct()
        return business_users

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(offer__user__username=self.value(), offer__user__type="business")
        return queryset


class OfferDetailAdminForm(admin.ModelAdmin):
    """
    Custom form for OfferDetail model to handle offer-related fields.
    """

    list_display = ("offer", "title", "price", "offer_type", "delivery_time_in_days")
    search_fields = ("offer__title", "title")
    list_filter = ("offer_type", BusinessUserOfferFilter, "offer__title")
    fields = (
        "offer",
        "title",
        "revisions",
        "delivery_time_in_days",
        "price",
        "offer_type",
        "features",
    )
    readonly_fields = ("offer", "offer_type", "id")


admin.site.register(Offer, OfferAdminForm)
admin.site.register(OfferDetail, OfferDetailAdminForm)
