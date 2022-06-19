from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist

from .models import ExtraLanguage, Section, Element, ExtraLangElement


EXTRA_LANGUAGES = ExtraLanguage.objects.all()
ELEMENTS = Element.objects.all()
ELEMENTS_EXTRA_LANGUAGE = ExtraLangElement.objects.all()


class JSON:
    # Сборка переводимых статических элементов страницы
    @staticmethod
    def collect_elements(lang, sections):
        if lang == 'ru':
            element_join = ELEMENTS.select_related('section').filter(section__name__in=sections)
            try:
                elements_json = {
                    'title': element_join.get(key='title').element,
                    'subtitle': element_join.get(key='subtitle').element,
                    'btn_about': element_join.get(key='btn-about').element,
                    'title_our_land': element_join.get(key='title-our-land').element,
                    'title_developments': element_join.get(key='title-developments').element,
                    'title_local_lore': element_join.get(key='title-local-lore').element,
                    'ref_footer': element_join.get(key='ref-footer').element,
                    'title_footer': element_join.get(key='title-footer').element,
                }
            except ObjectDoesNotExist:
                elements_json = {}
        else:
            element_join = ELEMENTS_EXTRA_LANGUAGE.select_related('language', 'element_rus', 'element_rus__section')\
                .filter(language__language_code=lang, element_rus__section__name__in=sections)
            try:
                elements_json = {
                    'title': element_join.get(element_rus__key='title').element,
                    'subtitle': element_join.get(element_rus__key='subtitle').element,
                    'btn_about': element_join.get(element_rus__key='btn-about').element,
                    'title_our_land': element_join.get(element_rus__key='title-our-land').element,
                    'title_developments': element_join.get(element_rus__key='title-developments').element,
                    'title_local_lore': element_join.get(element_rus__key='title-local-lore').element,
                    'ref_footer': element_join.get(element_rus__key='ref-footer').element,
                    'title_footer': element_join.get(element_rus__key='title-footer').element,
                }
            except ObjectDoesNotExist:
                elements_json = {}

        return elements_json


# Представление для получения списка языков и выбранного языка
class LanguageView:
    @staticmethod
    def get_languages():
        return EXTRA_LANGUAGES

    def get_selected_language(self):
        try:
            lang = self.kwargs.get('lang')
        except ObjectDoesNotExist:
            lang = 'ru'
        if not lang:
            lang = 'ru'

        return lang


class MainView(LanguageView, ListView):
    model = ExtraLanguage
    queryset = EXTRA_LANGUAGES
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        lang = LanguageView.get_selected_language(self)

        context['elements'] = JSON.collect_elements(lang, ['Main'])

        context['urls'] = {
            'lang': 'main'
        }

        return context