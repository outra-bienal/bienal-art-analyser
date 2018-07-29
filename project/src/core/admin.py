from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.contrib import messages
from django.urls import reverse

from src.core.models import AnalysedImage, Collection


class AdminFancyPreview(object):
    '''
    This will add a thumbnail image, a fancy preview for your Django admin
    list page. Let's say you have a model that has an image field. With this
    helper you will be able to display a thumbnail in the admin list page.
    For example:
        class ProductAdmin(AdminFancyPreview, admin.ModelAdmin):
            list_display = ('name', 'preview')
    By default we will assume that you have an image field named `image`.
    If that's not the case, you will have to customize things.
        class ProductAdmin(AdminFancyPreview, admin.ModelAdmin):
            list_display = ('name', 'preview')
            fancy_preview = {
                'image_field': 'photo',
                'image_size': '60px',
            }
    Note how you can customize the image field name but also the thumbnail size
    by defining a `fancy_preview` dictionary.
    '''

    def preview(self, obj):
        template = """<img src="{url}" style="max-width: {size};" />"""
        config = {
            'image_field': 'image',
            'image_size': '20em',
        }
        custom_config = getattr(self, 'fancy_preview', {})
        config.update(custom_config)
        image = getattr(obj, config['image_field'], None)
        url = image.url if image else ''
        content = template.format(url=url, size=config['image_size'])
        return format_html(content)
    preview.short_description=_('Preview')
    preview.allow_tags = True


class AnalysedImageInline(admin.TabularInline):
    model = AnalysedImage
    extra = 1
    suit_classes = 'suit-tab suit-tab-images'
    fields = ['image', 'collection']



class CollectionAdmin(admin.ModelAdmin):
    suit_form_tabs = (('colecao', _('Coleção')), ('images', _('Imagens')))
    list_display = ['title', 'date']
    inlines = [AnalysedImageInline]
    actions = ['run_analysis']
    fieldsets = (
        (None, {
            'fields': ('title', 'date'),
            'classes': ('suit-tab', 'suit-tab-colecao',),
        }),
        (_('Imagens'), {
            'classes': ('suit-tab', 'suit-tab-images',),
            'fields': []
        })
    )

    def run_analysis(self, request, queryset):
        for collection in queryset.all():
            collection.run_analysis()
        msg = "{} coleções foram enfileiradas para serem analisadas.".format(queryset.count())
        self.message_user(request, msg, messages.SUCCESS)
    run_analysis.short_description = _('Roda AI nas imagens da coleção')


class AnalysedImageAdmin(AdminFancyPreview, admin.ModelAdmin):
    list_display = ['id', 'preview', 'processed', 'link_to_collection']

    def link_to_collection(self, obj):
        link = reverse("admin:core_collection_change", args=[obj.collection.id])
        tag = '<a href="%s">%s</a>' % (link, obj.collection.title)
        return format_html(tag)
    link_to_collection.short_description = _('Coleção')


admin.site.register(Collection, CollectionAdmin)
admin.site.register(AnalysedImage, AnalysedImageAdmin)
