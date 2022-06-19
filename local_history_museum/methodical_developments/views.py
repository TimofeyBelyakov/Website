from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.apps import apps

from main.views import LanguageView
from .models import CategoryDevRu, CategoryDevExtraLang, Developments, DescriptionDevExtraLang


CATEGORIES_RU = CategoryDevRu.objects.all().order_by('id')
CATEGORIES_EXTRA_LANG = CategoryDevExtraLang.objects.all().order_by('id')
DEVELOPMENTS = Developments.objects.all().order_by('id')
DESCRIPTIONS_EXTRA_LANG = DescriptionDevExtraLang.objects.all()
ELEMENTS = apps.get_model('main', 'Element').objects.all()
ELEMENTS_EXTRA_LANGUAGE = apps.get_model('main', 'ExtraLangElement').objects.all()


# Класс для методов построения Json объектов
class JSON:
    # Сборка документов
    @staticmethod
    def collect_developments(lang, categories):
        development_join = DEVELOPMENTS.select_related('category')\
            .only('id', 'document', 'description', 'datetime', 'category__id')
        description_join = DESCRIPTIONS_EXTRA_LANG.select_related('language', 'document_rus')\
            .only('id', 'description', 'language__language_code', 'document_rus__id')
        development_json = []

        for category in categories:
            dev_desc = []
            if lang == 'ru':
                developments = development_join.filter(category__id=category.id)
                for development in developments:
                    item = {
                        'object': development,
                        'description': development.description
                    }
                    dev_desc.append(item)
            else:
                developments = development_join.filter(category__id=category.category_rus.id)
                for development in developments:
                    try:
                        description = description_join\
                            .get(language__language_code=lang, document_rus__id=development.id).description
                    except ObjectDoesNotExist:
                        description = None
                    item = {
                        'object': development,
                        'description': description
                    }
                    dev_desc.append(item)
            item = {
                'object': category,
                'count': developments.count(),
                'developments': dev_desc
            }
            development_json.append(item)

        return development_json

    # Сборка переводимых статических элементов страницы
    @staticmethod
    def collect_elements(lang, sections):
        if lang == 'ru':
            element_join = ELEMENTS.select_related('section').filter(section__name__in=sections)
            try:
                context_json = {
                    'tab': element_join.get(key='title-local-lore').element,
                    'title': element_join.get(key='title').element,
                    'subtitle': element_join.get(key='subtitle').element,
                    'btn_about': element_join.get(key='btn-about').element,
                    'btn_home': element_join.get(key='btn-home').element,
                    'title_filter': element_join.get(key='title-filter').element,
                    'btn_search': element_join.get(key='btn-search').element,
                    'checkbox_all': element_join.get(key='checkbox-all').element,
                    'ref_footer': element_join.get(key='ref-footer').element,
                    'title_footer': element_join.get(key='title-footer').element,
                }
            except ObjectDoesNotExist:
                context_json = {}
        else:
            element_join = ELEMENTS_EXTRA_LANGUAGE.select_related('language', 'element_rus', 'element_rus__section') \
                .filter(language__language_code=lang, element_rus__section__name__in=sections)
            try:
                context_json = {
                    'tab': element_join.get(element_rus__key='title-local-lore').element,
                    'title': element_join.get(element_rus__key='title').element,
                    'subtitle': element_join.get(element_rus__key='subtitle').element,
                    'btn_about': element_join.get(element_rus__key='btn-about').element,
                    'btn_home': element_join.get(element_rus__key='btn-home').element,
                    'title_filter': element_join.get(element_rus__key='title-filter').element,
                    'btn_search': element_join.get(element_rus__key='btn-search').element,
                    'checkbox_all': element_join.get(element_rus__key='checkbox-all').element,
                    'ref_footer': element_join.get(element_rus__key='ref-footer').element,
                    'title_footer': element_join.get(element_rus__key='title-footer').element,
                }
            except ObjectDoesNotExist:
                context_json = {}

        return context_json


# Представление для категорий
class CategoriesDevView:
    def get_categories(self):
        lang = self.kwargs.get('lang')
        document_join = DEVELOPMENTS.select_related('category').only('id', 'category__id')
        categories_list = []

        if lang == 'ru':
            for category in CATEGORIES_RU:
                documents_count = document_join.filter(category__id=category.id).count()
                if documents_count > 0:
                    categories_list.append(category.id)
            categories = CATEGORIES_RU.filter(id__in=categories_list)
        else:
            category_join = CATEGORIES_EXTRA_LANG.select_related('language', 'category_rus')\
                .only('id', 'category', 'language__language_code', 'category_rus__id')
            categories = category_join.filter(language__language_code=lang)
            for category in categories:
                documents_count = document_join.filter(category__id=category.category_rus.id).count()
                if documents_count > 0:
                    categories_list.append(category.id)
            categories = categories.filter(id__in=categories_list)

        return categories


# Представление для документов
class DevelopmentsListView(LanguageView, CategoriesDevView, ListView):
    context_object_name = 'categories'
    template_name = 'methodical_developments/base.html'
    paginate_by = 1

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        categories = CategoriesDevView.get_categories(self)
        category_json = JSON.collect_developments(lang, categories)

        return category_json

    def get_context_data(self, **kwargs):
        context = super(DevelopmentsListView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)
        else:
            context['page'] = ''

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Developments'])

        context['urls'] = {
            'lang': 'developments',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление для фильтрованных документов
class FilterDevelopmentsListView(LanguageView, CategoriesDevView, ListView):
    context_object_name = 'categories'
    template_name = 'methodical_developments/base.html'
    paginate_by = 1

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        categories = CategoriesDevView.get_categories(self).filter(category__in=self.request.GET.getlist('category'))
        category_json = JSON.collect_developments(lang, categories)

        return category_json

    def get_context_data(self, **kwargs):
        context = super(FilterDevelopmentsListView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)
        else:
            context['page'] = ''

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Developments'])

        context['urls'] = {
            'lang': 'developments',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
            'category': ''.join([f"category={x}&" for x in self.request.GET.getlist('category')]),
        }

        return context