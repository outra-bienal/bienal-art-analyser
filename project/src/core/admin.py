import json
from urllib.parse import urlencode

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from src.core.models import AnalysedImage, Collection


def preview(url, width='20em'):
    template = """<img src="{url}" style="max-width: {size};" />"""
    config = {
        'image_size': width,
    }
    content = template.format(url=url, size=config['image_size'])
    return format_html(content)


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
        return obj.processed
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


class AnalysedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'preview_list', 'processed', 'link_to_collection']
    list_filter = ['collection__title']
    exclude = ['collection', 'image', 'recokgnition_result', 'recokgnition_job_id', 'ibm_watson_result', 'ibm_watson_job_id', 'google_vision_result', 'google_vision_job_id', 'azure_vision_result', 'azure_vision_job_id', 'yolo_image', 'yolo_job_id']
    readonly_fields = ['link_to_collection', 'preview', 'yolo', 'aws', 'ibm', 'google', 'azure']

    def has_add_permission(self, request):
        return False

    def link_to_collection(self, obj):
        link = reverse("admin:core_collection_change", args=[obj.collection.id])
        tag = '<a href="%s">%s</a>' % (link, obj.collection.title)
        return format_html(tag)
    link_to_collection.short_description = _('Coleção')

    def preview_list(self, obj):
        return preview(obj.image.url)
    preview_list.short_description = _('Preview')

    def preview(self, obj):
        return preview(obj.image.url, "50em")
    preview.short_description = _('Preview')

    def yolo(self, obj):
        if obj.yolo_image:
            return preview(obj.yolo_image.url, "50em")
        return '---'

    def processed(self, obj):
        return obj.processed
    processed.short_description = _('Já análizado')
    processed.boolean = True

    def _display_result(self, result):
        if not result:
            return '---'
        else:
            content = json.dumps(result, indent=4, sort_keys=True).replace('\n', '<br/>')
            html = '<pre>{}</code>'.format(content)
            return mark_safe(html)

    def aws(self, obj):
        return self._display_result(obj.recokgnition_result)
    aws.short_description = _('AWS Recokgition')

    def ibm(self, obj):
        return self._display_result(obj.ibm_watson_result)
    ibm.short_description = _('IBM Watson')

    def google(self, obj):
        return self._display_result(obj.google_vision_result)
    google.short_description = _('Google Vision Cloud')

    def azure(self, obj):
        return self._display_result(obj.azure_vision_result)
    azure.short_description = _('Azure Computer Vision')


admin.site.register(Collection, CollectionAdmin)
admin.site.register(AnalysedImage, AnalysedImageAdmin)
