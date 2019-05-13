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
    max_num = 100


class CollectionAdmin(admin.ModelAdmin):
    suit_form_tabs = (('colecao', _('Coleção')), ('images', _('Imagens')))
    list_display = ['title', 'date', 'processed', 'link_to_images', 'public']
    readonly_fields = ['triggered_analysis']
    list_filter = ['public']
    inlines = [AnalysedImageInline]
    actions = ['run_analysis', 'generate_dense_cap_images']
    fieldsets = (
        (None, {
            'fields': ('title', 'date', 'public'),
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
        qs = urlencode({'collection': obj.id})
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

    def generate_dense_cap_images(self, request, queryset):
        for collection in queryset.all():
            collection.generate_dense_cap_images()
        msg = "Gerando imagens de DenseCap para {} coleções.".format(queryset.count())
        self.message_user(request, msg, messages.SUCCESS)
    generate_dense_cap_images.short_description = _('Gerar imagens do DenseCap')


from django.contrib.admin import SimpleListFilter

class CollectionFilter(SimpleListFilter):
    title = u'Coleçãoo'
    parameter_name = 'collection'

    def lookups(self, request, model_admin):
        collections = Collection.objects.all()
        if not request.user.is_superuser:
            collections = collections.filter(public=True)
        return [(c.id, c.title) for c in collections]

    def queryset(self, request, queryset):
        v = self.value()
        if not request.user.is_superuser:
            queryset = queryset.filter(collection__public=True)
        if v:
            return queryset.filter(collection=self.value())
        return queryset


class AnalysedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'preview_list', 'processed', 'link_to_collection']
    list_filter = [CollectionFilter]
    exclude = ['collection', 'image', 'recokgnition_result', 'recokgnition_job_id', 'ibm_watson_result', 'ibm_watson_job_id', 'deep_ai_result', 'deep_ai_job_id', 'google_vision_result', 'google_vision_job_id', 'azure_vision_result', 'azure_vision_job_id', 'yolo_image', 'yolo_job_id', 'detectron_image', 'clarifai_result', 'clarifai_job_id', 'dense_cap_job_id', 'dense_cap_image', 'dense_cap_full_image']
    readonly_fields = ['link_to_collection', 'preview', 'yolo', 'detectron', 'dense_cap', 'dense_cap_full', 'aws', 'ibm', 'google', 'azure', 'deep_ai', 'clarifai']

    def has_add_permission(self, request):
        return False

    def link_to_collection(self, obj):
        link = reverse("admin:core_collection_change", args=[obj.collection.id])
        tag = '<a href="{}">{} - ID ({})</a>'.format(link, obj.collection.title, obj.collection.id)
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

    def dense_cap(self, obj):
        if obj.dense_cap_image:
            return preview(obj.dense_cap_image.url, "50em")
        return '---'

    def dense_cap_full(self, obj):
        if obj.dense_cap_full_image:
            return preview(obj.dense_cap_full_image.url, "50em")
        return '---'

    def detectron(self, obj):
        if obj.detectron_image:
            return preview(obj.detectron_image.url, "50em")
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

    def deep_ai(self, obj):
        return self._display_result(obj.deep_ai_result)
    deep_ai.short_description = _('Deep AI')

    def clarifai(self, obj):
        return self._display_result(obj.clarifai_result)
    clarifai.short_description = _('Clarifai')

    def get_queryset(self, request):
        qs = super(AnalysedImageAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(collection__public=True)
        return qs


admin.site.register(Collection, CollectionAdmin)
admin.site.register(AnalysedImage, AnalysedImageAdmin)
