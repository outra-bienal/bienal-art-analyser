from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _

from src.core.models import AnalysedImage, Collection


class QuestionTagAdmin(admin.ModelAdmin):
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False


class AnalysedImageInline(admin.TabularInline):
    model = AnalysedImage
    extra = 1
    suit_classes = 'suit-tab suit-tab-images'
    fields = ['image', 'collection']


class CollectionAdmin(admin.ModelAdmin):
    suit_form_tabs = (('colecao', _('Coleção')), ('images', _('Imagens')))
    list_display = ['title', 'date']
    inlines = [AnalysedImageInline]
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





admin.site.register(Collection, CollectionAdmin)
