from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.db.models import Case, IntegerField, Value, When
from django.db.models import Q

from django.contrib import messages
from datetime import datetime

from main.views import LanguageView
from .models import CategoryRu, CategoryExtraLang, RegionRu, RegionExtraLang, ArticleRu, ArticleExtraLang, \
    Image, VideoRu, VideoExtraLang, Phone, Mail, Comment

# Импорт формы для комментариев
# from .forms import CommentForm


# Запросы к базе данных
EXTRA_LANGUAGES = apps.get_model('main', 'ExtraLanguage').objects.all().order_by('id')
CATEGORIES_RU = CategoryRu.objects.all().order_by('id')
CATEGORIES_EXTRA_LANG = CategoryExtraLang.objects.all().order_by('id')
REGIONS_RU = RegionRu.objects.all().order_by('id')
REGIONS_EXTRA_LANG = RegionExtraLang.objects.all().order_by('id')
ARTICLES_RU = ArticleRu.objects.all()
ARTICLES_EXTRA_LANG = ArticleExtraLang.objects.all()
VIDEOS_RU = VideoRu.objects.all().order_by('id')
VIDEOS_EXTRA_LANG = VideoExtraLang.objects.all().order_by('id')
IMAGES = Image.objects.all().order_by('id')
PHONES = Phone.objects.all().order_by('id')
MAILS = Mail.objects.all().order_by('id')
COMMENTS = Comment.objects.all().order_by('id')
ELEMENTS = apps.get_model('main', 'Element').objects.all()
ELEMENTS_EXTRA_LANGUAGE = apps.get_model('main', 'ExtraLangElement').objects.all()


# Класс для методов построения Json объектов
class JSON:
    # Сборка статьи
    @staticmethod
    def collect_article(lang, articles):
        image_join = IMAGES.select_related('article').only('id', 'image', 'article__url')
        video_ru_join = VIDEOS_RU.select_related('article').only('id', 'name_video', 'video', 'article__url')
        video_extra_lang_join = VIDEOS_EXTRA_LANG.select_related('language', 'video', 'video__article')\
            .only('id', 'name_video', 'video', 'language__language_code', 'video__article__url')

        article_json = []
        for article in articles:
            if lang == 'ru':
                images = image_join.filter(article__url=article.url)
                videos = video_ru_join.filter(article__url=article.url)
            else:
                images = image_join.filter(article__url=article.article_rus.url)
                videos = video_extra_lang_join\
                    .filter(language__language_code=lang, video__article__url=article.article_rus.url)

            item = {
                'object': article,
                'images': images,
                'videos': videos
            }
            article_json.append(item)

        return article_json

    # Сборка категорий
    @staticmethod
    def collect_categories(lang, articles, categories):
        category_json = []

        for categ in categories:
            if lang == 'ru':
                item = {
                    'category': categ.category,
                    'url': categ.url,
                    'count': articles.filter(category__url=categ.url).count()
                }
            else:
                item = {
                    'category': categ.category_rus.category,
                    'url': categ.category_rus.url,
                    'count': articles.filter(article_rus__category__url=categ.category_rus.url).count()
                }
            category_json.append(item)

        return category_json

    # Сборка непустых регионов
    @staticmethod
    def collect_regions(lang, articles, regions):
        regions_not_empty = []

        for reg in regions:
            if lang == 'ru':
                count = articles.filter(region__url=reg.url).count()
                item = {
                    'region': reg.region,
                    'url': reg.url,
                    'count': count
                }
            else:
                count = articles.filter(article_rus__region__url=reg.region_rus.url).count()
                item = {
                    'region': reg.region,
                    'url': reg.region_rus.url,
                    'count': count
                }

            if count > 0:
                regions_not_empty.append(item)

        return regions_not_empty

    # Сборка переводимых статических элементов страницы
    @staticmethod
    def collect_elements(lang, sections):
        if lang == 'ru':
            element_join = ELEMENTS.select_related('section').filter(section__name__in=sections)
            try:
                context_json = {
                    'tab': element_join.get(key='title-our-land').element,
                    'title': element_join.get(key='title').element,
                    'subtitle': element_join.get(key='subtitle').element,
                    'btn_about': element_join.get(key='btn-about').element,
                    'btn_home': element_join.get(key='btn-home').element,
                    'map': element_join.get(key='map').element,
                    'our_channel': element_join.get(key='our-channel').element,
                    'categories': element_join.get(key='categories').element,
                    'recent': element_join.get(key='recent').element,
                    'region': element_join.get(key='region').element,
                    'inp_search': element_join.get(key='inp-search').element,
                    'phone': element_join.get(key='phone').element,
                    'email': element_join.get(key='email').element,
                    'comments_title': element_join.get(key='comments-title').element,
                    'comment_answer': element_join.get(key='comment-answer').element,
                    'comment_send': element_join.get(key='comment-send').element,
                    'comment_name': element_join.get(key='comment-name').element,
                    'comment_text': element_join.get(key='comment-text').element,
                    'more_comments': element_join.get(key='more-comments').element,
                    'good_message': element_join.get(key='good-message').element,
                    'bad_message': element_join.get(key='bad-message').element,
                    'ref_footer': element_join.get(key='ref-footer').element,
                    'title_footer': element_join.get(key='title-footer').element,
                    'empty_article': element_join.get(key='empty-article').element,
                    'empty_search': element_join.get(key='empty-search').element,
                }
            except ObjectDoesNotExist:
                context_json = {}
        else:
            element_join = ELEMENTS_EXTRA_LANGUAGE.select_related('language', 'element_rus', 'element_rus__section') \
                .filter(language__language_code=lang, element_rus__section__name__in=sections)
            try:
                context_json = {
                    'tab': element_join.get(element_rus__key='title-our-land').element,
                    'title': element_join.get(element_rus__key='title').element,
                    'subtitle': element_join.get(element_rus__key='subtitle').element,
                    'btn_about': element_join.get(element_rus__key='btn-about').element,
                    'btn_home': element_join.get(element_rus__key='btn-home').element,
                    'map': element_join.get(element_rus__key='map').element,
                    'our_channel': element_join.get(element_rus__key='our-channel').element,
                    'categories': element_join.get(element_rus__key='categories').element,
                    'recent': element_join.get(element_rus__key='recent').element,
                    'region': element_join.get(element_rus__key='region').element,
                    'inp_search': element_join.get(element_rus__key='inp-search').element,
                    'phone': element_join.get(element_rus__key='phone').element,
                    'email': element_join.get(element_rus__key='email').element,
                    'comments_title': element_join.get(element_rus__key='comments-title').element,
                    'comment_answer': element_join.get(element_rus__key='comment-answer').element,
                    'comment_send': element_join.get(element_rus__key='comment-send').element,
                    'comment_name': element_join.get(element_rus__key='comment-name').element,
                    'comment_text': element_join.get(element_rus__key='comment-text').element,
                    'more_comments': element_join.get(element_rus__key='more-comments').element,
                    'good_message': element_join.get(element_rus__key='good-message').element,
                    'bad_message': element_join.get(element_rus__key='bad-message').element,
                    'ref_footer': element_join.get(element_rus__key='ref-footer').element,
                    'title_footer': element_join.get(element_rus__key='title-footer').element,
                    'empty_article': element_join.get(element_rus__key='empty-article').element,
                    'empty_search': element_join.get(element_rus__key='empty-search').element,
                }
            except ObjectDoesNotExist:
                context_json = {}

        return context_json


# Класс методов, возвращающих статьи
class ArticleView:
    articles_ru_join = ARTICLES_RU.select_related('region', 'category')
    articles_lang_join = ARTICLES_EXTRA_LANG.select_related('language', 'article_rus', 'article_rus__region',
                                                            'article_rus__category')

    # Возвращает статьи
    def get_articles(self):
        lang = self.kwargs.get('lang')

        if lang == 'ru':
            articles = ArticleView.articles_ru_join.filter(draft=False)
        else:
            articles = ArticleView.articles_lang_join.filter(language__language_code=lang, draft=False)\
                .only('id', 'title', 'article', 'draft', 'datetime', 'language__language_code', 'article_rus__map',
                      'article_rus__url', 'article_rus__region__url', 'article_rus__category__url')

        return articles

    # Возвращает названия последних 5 статей
    def get_last_articles(self):
        lang = self.kwargs.get('lang')
        try:
            reg = self.kwargs.get('reg')
        except ObjectDoesNotExist:
            reg = None

        if lang == 'ru':
            articles = ARTICLES_RU.filter(draft=False).only('id', 'title', 'draft', 'datetime')
            if reg is not None:
                articles = articles.filter(region__url=reg)
        else:
            articles = ARTICLES_EXTRA_LANG.select_related('language').filter(language__language_code=lang, draft=False)\
                .only('id', 'title', 'draft', 'datetime', 'language__language_code')
            if reg is not None:
                articles = articles.filter(article_rus__region__url=reg)

        return articles.order_by('-datetime')[:5]


# Класс методов, возвращающих категории статей
class CategoryView(ArticleView):
    # Возращает категории
    def get_category(self):
        lang = self.kwargs.get('lang')

        if lang == 'ru':
            categories = CATEGORIES_RU
        else:
            categories = CATEGORIES_EXTRA_LANG.select_related('language', 'category_rus')\
                .filter(language__language_code=lang)

        return categories

    # Возращает собранные категории
    def get_collected_category(self):
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        categories = CategoryView.get_category(self)
        articles = ArticleView.get_articles(self)

        if reg is not None:
            if lang == 'ru':
                articles = articles.filter(region__url=reg)
            else:
                articles = articles.filter(article_rus__region__url=reg)

        category_json = JSON.collect_categories(lang, articles, categories)

        return category_json


# Класс методов, возвращающих регионы
class RegionView(ArticleView):
    # Возвращает все регионы
    def get_regions(self):
        lang = self.kwargs.get('lang')

        if lang == 'ru':
            regions = REGIONS_RU
        else:
            region_join = REGIONS_EXTRA_LANG.select_related('language', 'region_rus') \
                .only('id', 'region', 'language__language_code', 'region_rus__blazon', 'region_rus__url')
            regions = region_join.filter(language__language_code=lang)

        return regions

    # Возвращает непустые регионы
    def get_not_empty_regions(self):
        lang = self.kwargs.get('lang')
        articles = ArticleView.get_articles(self)
        regions = RegionView.get_regions(self)

        regions_not_empty = JSON.collect_regions(lang, articles, regions)

        return regions_not_empty


# Представление изображений для определённой статьи
class ImageView:
    def get_images(self):
        art = self.kwargs.get('art')
        images = IMAGES.select_related('article').only('id', 'image', 'article__url').filter(article__url=art)

        return images


# Представление видео для определённой статьи
class VideoView:
    def get_videos(self):
        lang = self.kwargs.get('lang')
        art = self.kwargs.get('art')

        if lang == 'ru':
            video_join = VIDEOS_RU.select_related('article').only('id', 'name_video', 'video', 'article__url')
            videos = video_join.filter(article__url=art)
        else:
            video_join = VIDEOS_EXTRA_LANG.select_related('language', 'video', 'video__article') \
                .only('id', 'name_video', 'video', 'language__language_code', 'video__article__url')
            videos = video_join.filter(language__language_code=lang, video__article__url=art)

        return videos


# Представление контактов для определённой статьи
class ContactsView:
    def get_contacts(self):
        art = self.kwargs.get('art')
        phone_join = PHONES.select_related('article').only('id', 'telephone', 'article__url')
        mail_join = MAILS.select_related('article').only('id', 'email', 'article__url')

        contacts = {
            'phones': phone_join.filter(article__url=art),
            'mails': mail_join.filter(article__url=art)
        }

        return contacts


# Представление комментариев
class CommentView:
    def get_comments(self):
        art = self.kwargs.get('art')
        comment_join = COMMENTS.select_related('article')\
            .only('id', 'email', 'name', 'text', 'likes', 'datetime', 'draft', 'parent', 'article__url')
        comments = comment_join.filter(article__url=art, parent__isnull=True, draft=False)[:2]

        return comments

    def get_few_comments(self):
        comments = CommentView.get_comments(self)[:2]

        return comments

    def get_comments_count(self):
        art = self.kwargs.get('art')
        comment_join = COMMENTS.select_related('article') \
            .only('id', 'email', 'name', 'text', 'likes', 'datetime', 'draft', 'parent', 'article__url')
        count = comment_join.filter(article__url=art, draft=False).count()
        return count


# Представление всех районов
class RegionListView(LanguageView, RegionView, CategoryView, ListView):
    context_object_name = 'region_list'
    template_name = 'our_land/regions.html'

    def get_queryset(self):
        regions = RegionView.get_regions(self)

        return regions

    def get_context_data(self, **kwargs):
        context = super(RegionListView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Our-land'])

        context['urls'] = {
            'lang': 'our_land',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Детальное представление статьи
class ArticleDetailView(LanguageView, RegionView, CategoryView, ImageView, VideoView, ContactsView, CommentView,
                        DetailView):
    context_object_name = 'article'
    template_name = 'our_land/article.html'

    def get_object(self, queryset=None):
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        art = self.kwargs.get('art')
        articles = ArticleView.get_articles(self)

        try:
            if lang == 'ru':
                article = articles.get(region__url=reg, url=art)
            else:
                article = articles.get(article_rus__region__url=reg, article_rus__url=art)
        except ObjectDoesNotExist:
            article = None

        return article

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        art = self.kwargs.get('art')

        # Форма для комментариев
        # context['form'] = CommentForm()

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Our-land'])

        context['urls'] = {
            'region': reg,
            'article': art,
            'lang': 'article',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление статей по поиску
class SearchView(LanguageView, RegionView, CategoryView, ListView):
    context_object_name = 'article_list'
    template_name = 'our_land/articles.html'
    paginate_by = 3

    def get_queryset(self):
        q = self.request.GET.get('q')
        article_json = []

        if q:
            lang = self.kwargs.get('lang')
            articles = ArticleView.get_articles(self)
            articles_filter = articles.filter(
                Q(title__icontains=q) | Q(article__icontains=q)
            )
            article_json = JSON.collect_article(lang, articles_filter)

        return article_json

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        q = self.request.GET.get('q')
        page = self.request.GET.get('page')

        if q:
            context['search'] = q
        else:
            context['search'] = ''

        if page:
            context['page'] = 'page=' + str(page)

        context['elements'] = JSON.collect_elements(lang, ['Main', 'Our-land'])

        context['urls'] = {
            'q': 'q=' + str(q),
            'lang': 'search',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление статей по региону
class ArticleRegionView(LanguageView, RegionView, CategoryView, ArticleView, ListView):
    context_object_name = 'article_list'
    template_name = 'our_land/articles.html'
    paginate_by = 3

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        articles = ArticleView.get_articles(self)

        if lang == 'ru':
            articles_filter = articles.filter(region__url=reg).annotate(
                weight=Case(
                    When(category__url="general-info", then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )).order_by('weight', 'id')
        else:
            articles_filter = articles.filter(article_rus__region__url=reg).annotate(
                weight=Case(
                    When(article_rus__category__url="general-info", then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )).order_by('weight', 'id')

        articles_json = JSON.collect_article(lang, articles_filter)

        return articles_json

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ArticleRegionView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        regions = RegionView.get_regions(self)
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)

        if lang == 'ru':
            region = regions.get(url=reg)
        else:
            region = regions.get(region_rus__url=reg)

        context['object'] = region
        context['elements'] = JSON.collect_elements(lang, ['Main', 'Our-land'])

        context['urls'] = {
            'region': reg,
            'lang': 'region',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление статей по категории
class ArticleCategoryView(LanguageView, RegionView, CategoryView, ArticleView, ListView):
    context_object_name = 'article_list'
    template_name = 'our_land/articles.html'
    paginate_by = 3

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        categ = self.kwargs.get('categ')
        articles = ArticleView.get_articles(self)

        if lang == 'ru':
            articles_filter = articles.filter(category__url=categ)
        else:
            articles_filter = articles.filter(article_rus__category__url=categ)

        articles_json = JSON.collect_article(lang, articles_filter)

        return articles_json

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ArticleCategoryView, self).get_context_data(**kwargs)
        lang = self.kwargs.get('lang')
        categ = self.kwargs.get('categ')
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)

        if lang == 'ru':
            category = CategoryView.get_category(self).get(url=categ)
        else:
            category = CategoryView.get_category(self).get(language__language_code=lang, category_rus__url=categ)

        context['object'] = category
        context['elements'] = JSON.collect_elements(lang, ['Main', 'Our-land'])

        context['urls'] = {
            'category': categ,
            'lang': 'category',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление статей по категории
class ArticleRegionCategoryView(LanguageView, RegionView, CategoryView, ArticleView, ListView):
    context_object_name = 'article_list'
    template_name = 'our_land/articles.html'
    paginate_by = 3

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        categ = self.kwargs.get('categ')
        articles = ArticleView.get_articles(self)

        if lang == 'ru':
            articles_filter = articles.filter(region__url=reg, category__url=categ)
        else:
            articles_filter = articles.filter(article_rus__region__url=reg, article_rus__category__url=categ)

        articles_json = JSON.collect_article(lang, articles_filter)

        return articles_json

    def get_context_data(self, *, object_list=None, **kwargs):
        lang = self.kwargs.get('lang')
        reg = self.kwargs.get('reg')
        categ = self.kwargs.get('categ')
        context = super(ArticleRegionCategoryView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page')

        if page:
            context['page'] = 'page=' + str(page)

        if lang == 'ru':
            category = CategoryView.get_category(self).get(url=categ)
        else:
            category = CategoryView.get_category(self).get(language__language_code=lang, category_rus__url=categ)

        context['object'] = category
        context['elements'] = JSON.collect_elements(lang, ['Main', 'Our-land'])

        context['urls'] = {
            'region': reg,
            'category': categ,
            'lang': 'region_category',
            'home_ru': 'main_ru',
            'home_extra': 'main_extra_lang',
        }

        return context


# Представление для добавления комментариев
class AddComment(ArticleView, View):
    @staticmethod
    def post(request, lang):
        art = request.POST.get('art')
        article = ARTICLES_RU.get(url=art)

        form = CommentForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get('parent', None):
                form.parent_id = int(request.POST.get('parent'))
            form.article = article
            form.save()
            message = True
        else:
            message = False

        return JsonResponse({'message': message})


# Представление для динамической загрузки комментариев
class DynamicCommentsLoad(CommentView, View):
    @staticmethod
    def get(request, *args, **kwargs):
        last_comment_id = request.GET.get('lastCommId')
        art = request.GET.get('artUrl')

        comment_join = COMMENTS.select_related('article') \
            .only('id', 'email', 'name', 'text', 'likes', 'datetime', 'draft', 'parent__id', 'article__url')
        more_comments = comment_join.filter(pk__gt=int(last_comment_id), article__url=art, parent__isnull=True,
                                            draft=False)[:2]

        if not more_comments:
            return JsonResponse({'data': False})

        data = []
        for comment in more_comments:
            child_comments = comment.comment_set.all().filter(draft=False).order_by('datetime')[:1]
            children = []
            for child in child_comments:
                item = {
                    'id': child.id,
                    'email': child.email,
                    'name': child.name,
                    'text': child.text,
                    'likes': child.likes,
                    'datetime': child.datetime.strftime("%d.%m.%Y %H:%M"),
                    'parent': child.parent.id,
                    'article': child.article.url,
                    'draft': child.draft,
                }
                children.append(item)

            item = {
                'id': comment.id,
                'email': comment.email,
                'name': comment.name,
                'text': comment.text,
                'likes': comment.likes,
                'datetime': comment.datetime.strftime("%d.%m.%Y %H:%M"),
                'draft': comment.draft,
                'parent': comment.parent,
                'article': comment.article.url,
                'children': children
            }
            data.append(item)
        data[-1]['last-comment'] = True

        return JsonResponse({'data': data})


# Представление для динамической загрузки комментариев
class DynamicChildCommentsLoad(CommentView, View):
    @staticmethod
    def get(request, *args, **kwargs):
        last_comment_id = request.GET.get('lastChildCommId')
        comment_join = COMMENTS.select_related('article', 'parent') \
            .only('id', 'email', 'name', 'text', 'likes', 'datetime', 'draft', 'parent__id', 'article__url')
        try:
            last_comment = comment_join.get(id=last_comment_id)
            more_comments = comment_join.filter(pk__gt=int(last_comment_id), article__url=last_comment.article.url,
                                                parent__id=last_comment.parent.id, draft=False)[:1]
        except ObjectDoesNotExist:
            last_comment = None
            more_comments = None

        if not more_comments:
            return JsonResponse({'data': False})

        data = []
        for comment in more_comments:
            item = {
                'id': comment.id,
                'email': comment.email,
                'name': comment.name,
                'text': comment.text,
                'likes': comment.likes,
                'datetime': comment.datetime.strftime("%d.%m.%Y %H:%M"),
                'draft': comment.draft,
                'parent': comment.parent.id,
                'article': comment.article.url,
            }
            data.append(item)
        data[-1]['last-comment'] = True

        return JsonResponse({'data': data})