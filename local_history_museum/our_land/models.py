from django.db import models
from django.urls import reverse
from embed_video.fields import EmbedVideoField
from django.core.validators import *


def modify_fields(**kwargs):
    def wrap(cls):
        for field, prop_dict in kwargs.items():
            for prop, val in prop_dict.items():
                setattr(cls._meta.get_field(field), prop, val)
        return cls
    return wrap


# Валидация номера телефона
telephone = RegexValidator(
    r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$',
    'Телефон задан неверно.'
)


# Абстрактный класс категории
class Category(models.Model):
    category = models.CharField('Категория', max_length=100)

    class Meta:
        abstract = True


# Категории статей на русском
@modify_fields(
        category={
            'help_text': 'Добавьте категорию на русском языке'
        }
)
class CategoryRu(Category):
    url = models.SlugField('параметр URL', unique=True, max_length=160)

    def __str__(self):
        return self.category

    def get_absolute_url(self):
        return reverse('category', kwargs={'lang': 'ru', 'categ': self.url})

    class Meta:
        unique_together = ['category']
        ordering = ['id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# Категории статей на иностранных языках
@modify_fields(
        category={
            'verbose_name': 'Перевод категории',
            'help_text': 'Добавьте перевод категории на выбранный язык'
        }
)
class CategoryExtraLang(Category):
    language = models.ForeignKey('main.ExtraLanguage', on_delete=models.CASCADE, verbose_name='Язык')
    category_rus = models.ForeignKey(CategoryRu, on_delete=models.CASCADE, verbose_name='Категория', help_text='Выберите категорию, которую хотите перевести')

    def __str__(self):
        return f"{self.category}"

    def get_absolute_url(self):
        return reverse('category', kwargs={
            'lang': self.language.language_code,
            'categ': self.category_rus.url
        })

    class Meta:
        unique_together = ['category_rus', 'language']
        ordering = ['category_rus', 'language']
        verbose_name = 'Категория (ин. языки)'
        verbose_name_plural = 'Категории (ин. языки)'


# Абстрактный класс района
class Region(models.Model):
    region = models.CharField('Район', max_length=50)

    class Meta:
        abstract = True


# Район на русском
@modify_fields(
        region={
            'help_text': 'Добавьте название района на русском языке'
        }
)
class RegionRu(Region):
    blazon = models.ImageField('Герб', upload_to='our_land/blazons', default='our_land/blazons/default_blazon.png')
    map = models.TextField('Карта', help_text='Вставьте <iframe> с картой региона', blank=True, null=True)
    url = models.SlugField('параметр URL', unique=True, max_length=160)

    def __str__(self):
        return self.region

    def get_absolute_url(self):
        return reverse('region', kwargs={'lang': 'ru', 'reg': self.url})

    class Meta:
        unique_together = ['region']
        ordering = ['id']
        verbose_name = 'Район'
        verbose_name_plural = 'Районы'


# Район на иностранных языках
@modify_fields(
        region={
            'verbose_name': 'Перевод названия района',
            'help_text': 'Добавьте перевод названия района на выбранный язык'
        }
)
class RegionExtraLang(Region):
    language = models.ForeignKey('main.ExtraLanguage', on_delete=models.CASCADE, verbose_name='Язык')
    region_rus = models.ForeignKey(RegionRu, on_delete=models.CASCADE, verbose_name='Район', help_text='Выберите район, который хотите перевести')

    def __str__(self):
        return f"{self.region}"

    def get_absolute_url(self):
        return reverse('region', kwargs={'lang': self.language.language_code, 'reg': self.region_rus.url})

    class Meta:
        unique_together = ['region_rus', 'language']
        ordering = ['region_rus', 'language']
        verbose_name = 'Район (ин. языки)'
        verbose_name_plural = 'Районы (ин. языки)'


# Абстрактный класс статьи
class Article(models.Model):
    title = models.CharField('Название', max_length=50)
    article = models.TextField('Статья')
    draft = models.BooleanField('Черновик', default=False)
    datetime = models.DateTimeField('Дата', auto_now=False, auto_now_add=True)

    class Meta:
        abstract = True


# Статьи на русском
@modify_fields(
        title={
            'help_text': 'Добавьте название статьи на русском языке'
        },
        article={
            'help_text': 'На русском языке'
        }
)
class ArticleRu(Article):
    region = models.ForeignKey(RegionRu, on_delete=models.CASCADE, verbose_name='Район', help_text='Выберите район, к которому хотите добавить статью')
    category = models.ForeignKey(CategoryRu, on_delete=models.CASCADE, verbose_name='Категория', help_text='Выберите категорию статьи')
    map = models.TextField('Карта', help_text='Вставьте iframe с картой достопримечательности', blank=True, null=True)
    url = models.SlugField('параметр URL', unique=True, max_length=100)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse('article', kwargs={'lang': 'ru', 'reg': self.region.url, 'art': self.url })

    class Meta:
        unique_together = ['region', 'title']
        ordering = ['region', 'category', 'title']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'


# Статьи на иностранных языках
@modify_fields(
        title={
            'help_text': 'Добавьте название статьи на соответствующем языке'
        },
        article={
            'help_text': 'На соответствующем языке'
        }
)
class ArticleExtraLang(Article):
    language = models.ForeignKey('main.ExtraLanguage', on_delete=models.CASCADE, verbose_name='Язык')
    article_rus = models.ForeignKey(ArticleRu, on_delete=models.CASCADE, verbose_name='Статья', help_text='Выберите статью, которую хотите перевести')

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse('article', kwargs={'lang': self.language.language_code, 'reg': self.article_rus.region.url, 'art': self.article_rus.url })

    class Meta:
        unique_together = ['article_rus', 'language']
        ordering = ['article_rus', 'language']
        verbose_name = 'Статья (ин. языки)'
        verbose_name_plural = 'Статьи (ин. языки)'


# Фотографии
class Image(models.Model):
    article = models.ForeignKey(ArticleRu, on_delete=models.CASCADE, verbose_name='Статья', help_text='Выберите статью, к которой хотите добавить изображение')
    image = models.ImageField('Изображение', upload_to='our_land/articles')

    def __str__(self):
        return f"{self.image.name}"

    class Meta:
        ordering = ['article', 'image']
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


# Абстрактный класс видео
class Video(models.Model):
    name_video = models.CharField('Название видео', unique=False, max_length=100)

    class Meta:
        abstract = True


# Видео с названием на русском
@modify_fields(
        name_video={
            'help_text': 'Добавьте название видео на русском языке'
        }
)
class VideoRu(Video):
    article = models.ForeignKey( ArticleRu, on_delete=models.CASCADE, verbose_name='Статья', help_text='Выберите статью, к которой хотите добавить видео')
    video = EmbedVideoField('Ссылка на видео', max_length=1000, help_text='YouTube')

    def __str__(self):
        return f"{self.name_video}"

    class Meta:
        unique_together = ['article', 'name_video']
        ordering = ['article', 'name_video']
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'


# Видео с названием на иностранном языке
@modify_fields(
        name_video={
            'help_text': 'Добавьте название видео на соответствующем языке'
        }
)
class VideoExtraLang(Video):
    video = models.ForeignKey(VideoRu, on_delete=models.CASCADE, verbose_name='Видео', help_text='Выберите видео, название которого хотите перевести')
    language = models.ForeignKey('main.ExtraLanguage', on_delete=models.CASCADE, verbose_name='Язык')

    def __str__(self):
        return f"{self.name_video}"

    class Meta:
        unique_together = ['video', 'language']
        ordering = ['video', 'language']
        verbose_name = 'Видео (ин. языки)'
        verbose_name_plural = 'Видео (ин. языки)'


# Телефоны
class Phone(models.Model):
    telephone = models.CharField('Телефон', unique=False, max_length=20, validators=[telephone, MaxLengthValidator])
    article = models.ForeignKey(ArticleRu, on_delete=models.CASCADE, verbose_name='Статья', help_text='Выберите объект, к которому хотите добавить телефон')

    def __str__(self):
        return f"{self.telephone}"

    class Meta:
        ordering = ['article', 'telephone']
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'


# E-mail
class Mail(models.Model):
    email = models.EmailField('E-mail', unique=False, max_length=100)
    article = models.ForeignKey(ArticleRu, on_delete=models.CASCADE, verbose_name='Статья', help_text='Выберите объект, к которому хотите добавить e-mail')

    def __str__(self):
        return f"{self.email}"

    class Meta:
        ordering = ['article', 'email']
        verbose_name = 'E-mail'
        verbose_name_plural = 'E-mail'


# Отзывы
class Comment(models.Model):
    email = models.EmailField('E-mail', unique=False, max_length=100, blank=True, null=True)
    name = models.CharField('Имя', unique=False, max_length=100)
    text = models.TextField('Сообщение', max_length=5000)
    likes = models.SmallIntegerField('Рейтинг', default=0)
    datetime = models.DateTimeField('Дата', auto_now=False, auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='Родитель', blank=True, null=True)
    article = models.ForeignKey(ArticleRu, on_delete=models.CASCADE, verbose_name='Статья')
    draft = models.BooleanField('Черновик', default=True)

    def __str__(self):
        return f"{self.name} - {self.article}"

    def get_child_comments(self):
        return self.comment_set.all().filter(draft=False).order_by('datetime')[:1]

    class Meta:
        ordering = ['article', 'name', 'datetime']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'