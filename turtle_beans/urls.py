from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import (
    obtain_auth_token, EmailUserViewSet, CreateEmailUserViewSet,
    UpdateEmailUserViewSet, UpdateUserImageViewSet, CountryViewSet,
    StateViewSet, CityViewSet, ValidateUserView, RequestPasswordChange,
    ChangePassword, AppVersionViewSet)
from apps.coffee.views import (CoffeeImagesViewSet, PriceWithSizeViewSet,
                               CoffeeViewSet, CoffeeBgImageViewSet,
                               CoffeeWeightViewSet, CoffeeQTYViewSet,
                               CoffeeGrindTypesViewSet, CoffeeLogosViewSet,
                               FavouriteViewSet)
from apps.contacts.views import MessageViewSet, ReminderViewSet, TermsConditionsViewSet, ContactUsViewSet, ReportBugViewSet
from apps.orders.views import (CartViewSet, ShippingTypesViewSet,
                               ShippingViewSet, OrderPlacedViewSet,
                               RateReviewViewSet, RateReviewCommentsViewSet)
from apps.coupon_code.views import CouponViewSet
from apps.notifications.views import NotificationsViewSet
from apps.version.views import VersionViewSet
from .views import ResetPassword
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

router = routers.DefaultRouter()

router.register('create-user', CreateEmailUserViewSet, base_name='create-user')
router.register('update-user', UpdateEmailUserViewSet, base_name='update-user')
router.register('user-image', UpdateUserImageViewSet, base_name='user-image')
router.register('users', EmailUserViewSet, base_name='users')
router.register('country', CountryViewSet, base_name='country')
router.register('state', StateViewSet, base_name='state')
router.register('city', CityViewSet, base_name='city')
router.register('coffee', CoffeeViewSet, base_name='coffee')
router.register('coffee-weight',
                CoffeeWeightViewSet,
                base_name='coffee-weight')
router.register('coffee-grind-types',
                CoffeeGrindTypesViewSet,
                base_name='coffee-grind-types')
router.register('favourite', FavouriteViewSet, base_name='favourite')
router.register('message-chat', MessageViewSet, base_name='message-chat')
router.register('reminder', ReminderViewSet, base_name='reminder')
router.register('terms-conditions',
                TermsConditionsViewSet,
                base_name='terms-conditions')
router.register('report-bug', ReportBugViewSet, base_name='report-bug')
router.register('contact-us', ContactUsViewSet, base_name='contact-us')
router.register('coffee-images',
                CoffeeImagesViewSet,
                base_name='coffee-images')
router.register('coffee-logo', CoffeeLogosViewSet, base_name='coffee-logo')
router.register('cart', CartViewSet, base_name='cart')
router.register('shipping', ShippingViewSet, base_name='shipping')
router.register('order-placed', OrderPlacedViewSet, base_name='order-placed')
router.register('rate-review', RateReviewViewSet, base_name='rate-review')
router.register('coupon', CouponViewSet, base_name='coupon')
router.register('qty', CoffeeQTYViewSet, base_name='qty')
router.register('notifications',
                NotificationsViewSet,
                base_name='notifications')
router.register('shipping-types',
                ShippingTypesViewSet,
                base_name='shipping-types')
router.register('coffee-bg-image',
                CoffeeBgImageViewSet,
                base_name='coffee-bg-image')
router.register('rate-review-comments', RateReviewCommentsViewSet,
                'rate-review-comments')
router.register('price-with-size', PriceWithSizeViewSet)
router.register('version', VersionViewSet)

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include(
        'jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', obtain_auth_token),
    url(r'^admin/', admin.site.urls),
    url(r'reset-password/(?P<email>[a-zA-Z0-9-.+@_]+)/$',
        RequestPasswordChange.as_view(),
        name='reset-password'),
    url(r'reset/(?P<validation_key>[a-z0-9\-]+)/$',
        ResetPassword.as_view(),
        name='reset-request'),
    url(r'^api/change-password/$', ChangePassword.as_view()),
    url(r'^api/version-data/$', AppVersionViewSet.as_view()),
    url(r'validate/(?P<validation_key>[a-z0-9\-]+)/$',
        ValidateUserView.as_view(),
        name='user-validation'),
    url(r'^$', schema_view)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
