import os
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import CategoryDocRu, CategoryDocExtraLang, Document, DescriptionDocExtraLang


class CategoryDocExtraLangInline(admin.TabularInline):
    model = CategoryDocExtraLang
    fields = ['language', 'category']
    extra = 1


class DescriptionDocExtraLangInline(admin.TabularInline):
    model = DescriptionDocExtraLang
    extra = 1


@admin.register(CategoryDocRu)
class CategoryDocRuAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'url']
    list_display_links = ['category']
    inlines = [
        CategoryDocExtraLangInline
    ]


@admin.register(CategoryDocExtraLang)
class CategoryDocExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'category_rus', 'language']
    list_display_links = ['category']
    list_filter = ['language']
    fields = ['category_rus', 'language', 'category']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'get_file', 'datetime']
    list_display_links = ['category']
    list_filter = ['category']
    fields = ['category', 'document', 'description', 'datetime']
    readonly_fields = ['datetime']
    inlines = [
        DescriptionDocExtraLangInline
    ]

    def get_file(self, obj):
        return mark_safe(f'<a href={obj.document.url}>{os.path.basename(obj.document.name)}</a>')

    get_file.short_description = 'Документ'


@admin.register(DescriptionDocExtraLang)
class DescriptionDocExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'language']
    list_display_links = ['get_name']

    def get_name(self, obj):
        return mark_safe(f'{obj.document_rus.category} - {os.path.basename(obj.document_rus.document.name)}')

    get_name.short_description = 'Документ'