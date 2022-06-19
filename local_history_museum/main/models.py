from django.db import models
from django.urls import reverse
from django.core.validators import *


# Валидация кода языка
code = RegexValidator(
    r'^[a-z]{2}$',
    'Код языка задан неверно.'
)


# Дополнительные языки
class ExtraLanguage(models.Model):
    language = models.CharField('Язык', max_length=50, unique=True, help_text='С заглавной буквы на соответствующем языке')
    language_code = models.SlugField('Код языка', max_length=2, unique=True, validators=[code], help_text='В соответствии со стандартом ISO 639-1')
    flag = models.ImageField('Флаг', upload_to='main/flags', default='main/flags/empty-flag.png', help_text='Размер 16x11')

    def __str__(self):
        return self.language

    def get_absolute_url(self):
        return reverse('main_extra_lang', kwargs={'lang': self.language_code})

    class Meta:
        ordering = ['id']
        verbose_name = 'Дополнительный язык'
        verbose_name_plural = 'Дополнительные языки'


# Разделы сайта
class Section(models.Model):
    name = models.SlugField('Раздел', max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Раздел сайта'
        verbose_name_plural = 'Разделы сайта'


# Элементы сайта
class Element(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name='Раздел')
    key = models.SlugField('Ключ', max_length=50, unique=True)
    element = models.TextField('Элемент сайта', unique=False)

    def __str__(self):
        return f'{self.section} - {self.key}'

    class Meta:
        unique_together = ['section', 'key']
        ordering = ['section', 'id']
        verbose_name = 'Элемент сайта'
        verbose_name_plural = 'Элементы сайта'


# Элементы сайта на ин. языках
class ExtraLangElement(models.Model):
    language = models.ForeignKey(ExtraLanguage, on_delete=models.CASCADE, verbose_name='Язык')
    element_rus = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name='Элемент сайта')
    element = models.TextField('Перевод элемента', unique=False)

    def __str__(self):
        return self.element

    class Meta:
        unique_together = ['element_rus', 'language']
        ordering = ['element_rus', 'language']
        verbose_name = 'Элемент сайта (ин. языки)'
        verbose_name_plural = 'Элементы сайта (ин. языки)'
