import os
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import CategoryDevRu, CategoryDevExtraLang, Developments, DescriptionDevExtraLang


class CategoryDevExtraLangInline(admin.TabularInline):
    model = CategoryDevExtraLang
    fields = ['language', 'category']
    extra = 1


class DescriptionDevExtraLangInline(admin.TabularInline):
    model = DescriptionDevExtraLang
    extra = 1


@admin.register(CategoryDevRu)
class CategoryDevRuAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'url']
    list_display_links = ['category']
    inlines = [
        CategoryDevExtraLangInline
    ]


@admin.register(CategoryDevExtraLang)
class CategoryDevExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'category_rus', 'language']
    list_display_links = ['category']
    list_filter = ['language']
    fields = ['category_rus', 'language', 'category']


@admin.register(Developments)
class DevelopmentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'get_file', 'datetime']
    list_display_links = ['category']
    list_filter = ['category']
    fields = ['category', 'document', 'description', 'datetime']
    readonly_fields = ['datetime']
    inlines = [
        DescriptionDevExtraLangInline
    ]

    def get_file(self, obj):
        return mark_safe(f'<a href={obj.document.url}>{os.path.basename(obj.document.name)}</a>')

    get_file.short_description = 'Документ'


@admin.register(DescriptionDevExtraLang)
class DescriptionDevExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'language']
    list_display_links = ['get_name']

    def get_name(self, obj):
        return mark_safe(f'{obj.document_rus.category} - {os.path.basename(obj.document_rus.document.name)}')

    get_name.short_description = 'Документ'
