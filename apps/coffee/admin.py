from django.contrib import admin

from .models import Coffee, CoffeeImages, CoffeeWeight, CoffeeQTY, CoffeeGrindTypes, CoffeeLogos, Favourite, PriceWithSize
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.encoding import force_text


class CoffeeImagesAdmin(admin.ModelAdmin):
    list_display = ['image', 'coffee']
    list_filter = ['coffee',]


def get_picture_preview(obj):
    if obj.pk:  # if object has already been saved and has a primary key, show picture preview
        return """<a href="{src}" target="_blank"><img src="{src}" style="max-width: 200px; max-height: 200px;" /></a>""".format(
            src=obj.image.url,
        )
    return _("(choose a picture and save and continue editing to see the preview)")
get_picture_preview.allow_tags = True
get_picture_preview.short_description = _("Picture Preview")


class PictureInline(admin.StackedInline):
    model = CoffeeImages
    extra = 0
    fields = ["get_edit_link", "coffee", "image", get_picture_preview]
    readonly_fields = ["get_edit_link", get_picture_preview]

    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[force_text(obj.pk)])
            return """<a href="{url}">{text}</a>""".format(
                url=url,
                text=_("Edit this %s separately") % obj._meta.verbose_name,
            )
        return _("(save and continue editing to create a link)")
    get_edit_link.short_description = _("Edit link")
    get_edit_link.allow_tags = True



class CoffeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'grind', 'is_sale', 'coffee_from']
    list_filter = ['grind', 'is_sale']
    search_fields = ('name', 'description')
    inlines = [PictureInline]

class FavouriteAdmin(admin.ModelAdmin):
    list_display = ['coffee', 'buyer']
    list_filter = ['coffee', 'buyer']
    search_fields = ('coffee', 'buyer')

class CoffeeWeightAdmin(admin.ModelAdmin):
    list_display = ['weight', 'weight_in_lb', 'country', 'group']

class PriceWithSizeAdmin(admin.ModelAdmin):
    list_display = ['coffee', 'weight', 'price', 'shipping_charge', 'inter_shipping_charge']
    list_filter = ['coffee',]
    search_fields = ('coffee',)


admin.site.register(Coffee, CoffeeAdmin)
admin.site.register(CoffeeImages, CoffeeImagesAdmin)
admin.site.register(CoffeeWeight, CoffeeWeightAdmin)
admin.site.register(CoffeeQTY)
admin.site.register(CoffeeGrindTypes)
admin.site.register(CoffeeLogos)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(PriceWithSize, PriceWithSizeAdmin)
