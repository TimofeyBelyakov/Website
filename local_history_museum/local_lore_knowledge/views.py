from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.apps import apps
from django.http import JsonResponse

from main.views import LanguageView
from .models import CategoryDocRu, CategoryDocExtraLang, Document, DescriptionDocExtraLang


CATEGORIES_RU = CategoryDocRu.objects.all().order_by('id')
CATEGORIES_EXTRA_LANG = CategoryDocExtraLang.objects.all().order_by('id')
DOCUMENTS = Document.objects.all().order_by('id')
DESCRIPTIONS_EXTRA_LANG = DescriptionDocExtraLang.objects.all()
ELEMENTS = apps.get_model('main', 'Element').objects.all()
ELEMENTS_EXTRA_LANGUAGE = apps.get_model('main', 'ExtraLangElement').objects.all()


# Класс для методов построения Json объектов
class JSON:
    # Сборка документов и описаний
    @staticmethod
    def collect_local_lore(lang, categories):
        document_join = DOCUMENTS.select_related('category')\
            .only('id', 'document', 'description', 'datetime', 'category__id')
        description_join = DESCRIPTIONS_EXTRA_LANG.select_related('language', 'document_rus')\
            .only('id', 'description', 'language__language_code', 'document_rus__id')
        document_json = []

        for category in categories:
            doc_desc = []
            if lang == 'ru':
                documents = document_join.filter(category__id=category.id)
                for document in documents:
                    item = {
                        'object': document,
                        'description': document.description
                    }
                    doc_desc.append(item)
            else:
                documents = document_join.filter(category__id=category.category_rus.id)
                for document in documents:
                    try:
                        description = description_join\
                            .get(language__language_code=lang, document_rus__id=document.id).description
                    except ObjectDoesNotExist:
                        description = None
                    item = {
                        'object': document,
                        'description': description
                    }
                    doc_desc.append(item)
            item = {
                'object': category,
                'count': documents.count(),
                'local_lore': doc_desc
            }
            document_json.append(item)

        return document_json

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
            element_join = ELEMENTS_EXTRA_LANGUAGE.select_related('language', 'element_rus', 'element_rus__section')\
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
class CategoriesDocView:
    # Возвращает категории, у которых есть документы
    def get_categories(self):
        lang = self.kwargs.get('lang')
        document_join = DOCUMENTS.select_related('category').only('id', 'category__id')
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
class LocalLoreListView(LanguageView, CategoriesDocView, ListView):
    context_object_name = 'categories'
    template_name = 'local_lore_knowledge/base.html'
    paginate_by = 1

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        categories = CategoriesDocView.get_categories(self)
        category_json = JSON.collect_local_lore(lang, categories)

        return category_json

    def get_context_data(self, **kwargs):
        context = super(LocalLoreListView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)
        else:
            context['page'] = ''

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Local-lore'])

        context['urls'] = {
            'lang': 'local_lore',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление для фильтрованных документов
class FilterLocalLoreView(LanguageView, CategoriesDocView, ListView):
    context_object_name = 'categories'
    template_name = 'local_lore_knowledge/base.html'
    paginate_by = 1

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        categories = CategoriesDocView.get_categories(self) \
            .filter(category__in=self.request.GET.getlist('category'))
        category_json = JSON.collect_local_lore(lang, categories)

        return category_json

    def get_context_data(self, **kwargs):
        context = super(FilterLocalLoreView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)
        else:
            context['page'] = ''

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Local-lore'])

        context['urls'] = {
            'lang': 'local_lore',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
            'category': ''.join([f"category={x}&" for x in self.request.GET.getlist('category')]),
        }

        return context