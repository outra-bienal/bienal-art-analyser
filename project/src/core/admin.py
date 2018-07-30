from urllib.parse import urlencode

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe

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
    extra = 5
    suit_classes = 'suit-tab suit-tab-images'
    fields = ['image', 'collection']


class CollectionAdmin(admin.ModelAdmin):
    suit_form_tabs = (('colecao', _('Coleção')), ('images', _('Imagens')))
    list_display = ['title', 'date', 'processed', 'link_to_images']
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

    def processed(self, obj):
        return all([i.processed for i in obj.analysed_images.all()])
    processed.short_description = _('Já análizado')
    processed.boolean = True

    def link_to_images(self, obj):
        qs = urlencode({'collection__title': obj.title})
        link = reverse("admin:core_analysedimage_changelist") + '?' + qs
        tag = '<a href="%s">%s</a>' % (link, _("Listar imagens"))
        return format_html(tag)
    link_to_images.short_description = _('Imagens')

    def run_analysis(self, request, queryset):
        for collection in queryset.all():
            collection.run_analysis()
        msg = "{} coleções foram enfileiradas para serem analisadas.".format(queryset.count())
        self.message_user(request, msg, messages.SUCCESS)
    run_analysis.short_description = _('Roda AI nas imagens da coleção')


class AnalysedImageAdmin(AdminFancyPreview, admin.ModelAdmin):
    list_display = ['id', 'preview', 'processed', 'link_to_collection']
    list_filter = ['collection__title']
    exclude = ['job_id', 'collection', 'image', 'recokgnition_result']
    readonly_fields = ['link_to_collection', 'preview', 'aws']

    def link_to_collection(self, obj):
        link = reverse("admin:core_collection_change", args=[obj.collection.id])
        tag = '<a href="%s">%s</a>' % (link, obj.collection.title)
        return format_html(tag)
    link_to_collection.short_description = _('Coleção')

    def processed(self, obj):
        return obj.processed
    processed.short_description = _('Já análizado')
    processed.boolean = True

    def aws(self, obj):
        if not obj.recokgnition_result:
            return '---'
        else:
            import json
            content = json.dumps(obj.recokgnition_result, indent=4, sort_keys=True).replace('\n', '<br/>')
            html = '<pre>{}</code>'.format(content)
            return mark_safe(html)
    aws.short_description = _('AWS Recokgition')


admin.site.register(Collection, CollectionAdmin)
admin.site.register(AnalysedImage, AnalysedImageAdmin)
