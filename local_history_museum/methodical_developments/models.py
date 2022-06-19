import os
from django.db import models


def modify_fields(**kwargs):
    def wrap(cls):
        for field, prop_dict in kwargs.items():
            for prop, val in prop_dict.items():
                setattr(cls._meta.get_field(field), prop, val)
        return cls
    return wrap


# Абстрактный класс категории
class CategoryDev(models.Model):
    category = models.CharField('Категория', max_length=100)

    class Meta:
        abstract = True


# Категории документов на русском
@modify_fields(
        category={
            'help_text': 'Добавьте категорию на русском языке'
        }
)
class CategoryDevRu(CategoryDev):
    url = models.SlugField('параметр URL', unique=True, max_length=160)

    def __str__(self):
        return self.category

    class Meta:
        unique_together = ['category']
        ordering = ['id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# Категории документов на иностранных языках
@modify_fields(
        category={
            'verbose_name': 'Перевод категории',
            'help_text': 'Добавьте перевод категории на выбранный язык'
        }
)
class CategoryDevExtraLang(CategoryDev):
    language = models.ForeignKey('main.ExtraLanguage', on_delete=models.CASCADE, verbose_name='Язык')
    category_rus = models.ForeignKey(CategoryDevRu, on_delete=models.CASCADE, verbose_name='Категория', help_text='Выберите категорию, которую хотите перевести')

    def __str__(self):
        return f"{self.category}"

    class Meta:
        unique_together = ['category_rus', 'language']
        ordering = ['category_rus', 'language']
        verbose_name = 'Категория (ин. языки)'
        verbose_name_plural = 'Категории (ин. языки)'


# Документы
class Developments(models.Model):
    category = models.ForeignKey(CategoryDevRu, on_delete=models.CASCADE, verbose_name='Категория')
    document = models.FileField('Документ', upload_to='developments/%Y/%m/', max_length=100)
    description = models.TextField('Описание', blank=True, null=True)
    datetime = models.DateTimeField('Дата', auto_now=False, auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.document.name)

    def filename(self):
        return os.path.basename(self.document.name)

    class Meta:
        unique_together = ['category', 'document']
        ordering = ['category', 'document']
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


# Описания на ин. языках
class DescriptionDevExtraLang(models.Model):
    document_rus = models.ForeignKey(Developments, on_delete=models.CASCADE, verbose_name='Документ')
    language = models.ForeignKey('main.ExtraLanguage', on_delete=models.CASCADE, verbose_name='Язык')
    description = models.TextField('Перевод описания')

    class Meta:
        unique_together = ['document_rus', 'language']
        ordering = ['document_rus', 'language']
        verbose_name = 'Описание (ин. языки)'
        verbose_name_plural = 'Описания (ин. языки)'