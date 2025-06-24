from django.contrib import admin
from django.contrib.auth import get_user_model

from reviews_app.models import Review

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


class ReviewerUserFilter(admin.SimpleListFilter):
    title = "Reviewer User"
    parameter_name = "reviewer_user"

    def lookups(self, request, model_admin):
        reviewer_users = User.objects.filter(type="customer").values_list("username", "username").distinct()
        return reviewer_users

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(reviewer__username=self.value(), reviewer__type="customer")
        return queryset


class ReviewAdminForm(admin.ModelAdmin):
    """
    Custom form for Review model to handle user-related fields.
    """

    list_display = ("business_user", "id", "reviewer", "rating", "created_at")
    search_fields = (
        "rating",
        "business_user__username",
        "reviewer__username",
    )
    list_filter = (ReviewerUserFilter, BusinessUserFilter, "rating", "created_at")
    fields = ("business_user", "id", "reviewer", "rating", "created_at", "description", "updated_at")
    readonly_fields = ("created_at", "business_user", "id", "reviewer", "updated_at")


admin.site.register(Review, ReviewAdminForm)
