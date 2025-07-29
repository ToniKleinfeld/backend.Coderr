from django import forms
from django.contrib import admin
from profiles_app.models import Profile


class ProfileAdminForm(forms.ModelForm):

    first_name = forms.CharField(max_length=150, required=False, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)

        if commit:
            user = profile.user
            user.first_name = self.cleaned_data.get("first_name", "")
            user.last_name = self.cleaned_data.get("last_name", "")

            user.save()

            profile.save()

        return profile


class CustomAdmin(admin.ModelAdmin):
    """
    Custom admin class for Profile model
    """

    form = ProfileAdminForm

    list_display = ("username", "id", "first_name", "last_name", "email", "type", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    list_filter = ("user__type",)

    fields = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "file",
        "location",
        "tel",
        "description",
        "working_hours",
        "type",
        "created_at",
    )

    readonly_fields = ("id", "created_at", "username", "type", "email")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")


admin.site.register(Profile, CustomAdmin)
