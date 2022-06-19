from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ExtraLanguage, Section, Element, ExtraLangElement


class ElementInline(admin.StackedInline):
    model = Element
    extra = 1


class ExtraLangElementInline(admin.TabularInline):
    model = ExtraLangElement
    extra = 1


@admin.register(ExtraLanguage)
class ExtraLanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'language_code', 'get_image']
    list_display_links = ['language']
    fields = ['language', 'language_code', ('get_image', 'flag')]
    readonly_fields = ['get_image']

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.flag.url} width="16" height="11">')

    get_image.short_description = 'Флаг'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']
    inlines = [ElementInline]


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['id', 'element', 'key', 'section']
    list_display_links = ['element']
    inlines = [ExtraLangElementInline]


@admin.register(ExtraLangElement)
class ExtraLangElementAdmin(admin.ModelAdmin):
    list_display = ['id', 'element', 'element_rus', 'language']
    list_display_links = ['element']


admin.site.site_title = 'Краеведческий образовательный сайт КГУ'
admin.site.site_header = 'Краеведческий образовательный сайт КГУ'