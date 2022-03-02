from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
# Register your models here.
"""
the CustomUser should have forms for both creating a new CustomUser
and updating an existing CustomUser
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import EmailUser, Country, State, City, GroupCountry, AppVersion, COFTOUSD


class EmailUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    def __init__(self, *args, **kargs):
        super(EmailUserCreationForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = EmailUser
        fields = '__all__'


class EmailUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    def __init__(self, *args, **kargs):
        super(EmailUserChangeForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = EmailUser
        fields = '__all__'


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailUser
from django.db.models import Q


class UserTypeListFilter(admin.SimpleListFilter):
    title = _('User Type')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('seller', _('Seller')),
            ('buyer', _('Buyer')),
        )
        #zincovit  2 ,ivormacin 12 mg 1 (3 days), doxycyclin 500 mg 1-1(5days)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'seller':
            return queryset.filter(is_seller=True)
        if self.value() == 'buyer':
            return queryset.filter(is_buyer=True)


class EmailUserAdmin(UserAdmin):
    """
    The following attributes may need to be overridden if your User's
    fields don't match up with the built-in User:
    form
    add_form
    change_password_form
    list_display
    list_filter
    fieldsets
    add_fieldsets
    search_fields
    ordering
    filter_horizontal
    """
    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    # don't need to override change_password_form

    list_display = ('email', 'first_name', 'last_name', 'is_superuser',
                    'is_seller', 'is_buyer', 'is_seller_approved')
    list_filter = (UserTypeListFilter, )
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'image', 'birth_date',
                       'phone_number', 'address_line_1', 'address_line_2',
                       'postal_code', 'profile_description')
        }),
        ('Location', {
            'fields': ('country', 'state', 'city')
        }),
        ('Permissions', {
            'fields': ('is_seller_approved', 'is_seller', 'is_buyer',
                       'is_superuser', 'validated_at')
        }),
        ('Company Details', {
            'fields': ('company_name', 'company_country', 'ABN',
                       'company_logo', 'background_image')
        }),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('email', 'password1', 'password2')
    }), )
    search_fields = ('email', )
    ordering = ('email', )
    filter_horizontal = ()


admin.site.register(EmailUser, EmailUserAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_country', 'currency_symbol',
                    'weight_format', 'braintree_merchanr_id', 'rate')
    list_filter = ('group_country', )
    search_fields = ('name', )


class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country', )
    search_fields = ('name', )


class CityAdmin(admin.ModelAdmin):
    list_display = ('postcode', 'name', 'state', 'country')
    list_filter = ('state', 'country')
    search_fields = ('postcode', 'name')


admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(GroupCountry)
admin.site.register(AppVersion)
admin.site.register(COFTOUSD)
