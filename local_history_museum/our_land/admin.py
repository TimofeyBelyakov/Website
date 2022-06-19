from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe
from .models import CategoryRu, CategoryExtraLang, RegionRu, RegionExtraLang, ArticleRu, ArticleExtraLang, \
    Image, VideoRu, VideoExtraLang, Phone, Mail # Comment


class ArticleRuAdminForm(forms.ModelForm):
    article = forms.CharField(label='Статья', widget=CKEditorUploadingWidget())

    class Meta:
        model = ArticleRu
        fields = '__all__'


class ArticleExtraLangAdminForm(forms.ModelForm):
    article = forms.CharField(label='Перевод статьи', widget=CKEditorUploadingWidget())

    class Meta:
        model = ArticleExtraLang
        fields = '__all__'


class CategoryExtraLangInline(admin.TabularInline):
    model = CategoryExtraLang
    fields = ['language', 'category']
    extra = 1


class RegionExtraLangInline(admin.TabularInline):
    model = RegionExtraLang
    extra = 1


class ArticleExtraLangInline(admin.StackedInline):
    form = ArticleExtraLangAdminForm
    model = ArticleExtraLang
    extra = 1
    fields = ['language', 'title', 'article', 'draft']


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = [('get_image', 'image')]
    readonly_fields = ['get_image']

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="75">')

    get_image.short_description = 'Изображение'


class VideoRuInline(admin.TabularInline):
    model = VideoRu
    extra = 1


class VideoExtraLangInline(admin.TabularInline):
    model = VideoExtraLang
    fields = ['language', 'name_video']
    extra = 1


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


class MailInline(admin.TabularInline):
    model = Mail
    extra = 1


@admin.register(CategoryRu)
class CategoryRuAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'url']
    list_display_links = ['category']
    inlines = [
        CategoryExtraLangInline
    ]


@admin.register(CategoryExtraLang)
class CategoryExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'category_rus', 'language']
    list_display_links = ['category']
    list_filter = ['language']
    fields = ['category_rus', 'language', 'category']


@admin.register(RegionRu)
class RegionRuAdmin(admin.ModelAdmin):
    list_display = ['id', 'region', 'url', 'get_image']
    list_display_links = ['region']
    fields = ['region', 'url', ('get_image', 'blazon')]
    readonly_fields = ['get_image']
    inlines = [
        RegionExtraLangInline
    ]

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.blazon.url} width="50" height="60">')

    get_image.short_description = 'Герб'


@admin.register(RegionExtraLang)
class RegionExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'region', 'region_rus', 'language']
    list_display_links = ['region']
    list_filter = ['language']
    fields = ['region_rus', 'language', 'region']


@admin.register(ArticleRu)
class ArticleRuAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'region', 'category', 'url', 'draft']
    list_display_links = ['title']
    list_filter = ['region', 'category']
    list_editable = ['draft']
    fields = ['title', 'article', 'map', 'draft', 'region', 'category', 'url', 'datetime']
    readonly_fields = ['datetime']
    actions = ['publish', 'unpublish']
    form = ArticleRuAdminForm
    inlines = [
        ArticleExtraLangInline,
        ImageInline,
        VideoRuInline,
        PhoneInline,
        MailInline
    ]
    save_on_top = True
    save_as = True

    def publish(self, request, queryset):
        row_update = queryset.update(draft=False)
        if row_update == '1':
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')

    def unpublish(self, request, queryset):
        row_update = queryset.update(draft=True)
        if row_update == '1':
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')

    publish.short_description = 'Опубликовать'
    publish.allowed_permissions = ('change', )

    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change', )


@admin.register(ArticleExtraLang)
class ArticleExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'article_rus', 'language', 'draft']
    list_display_links = ['title']
    list_filter = ['language']
    list_editable = ['draft']
    fields = ['article_rus', 'language', 'title', 'article', 'draft', 'datetime']
    readonly_fields = ['datetime']
    actions = ['publish', 'unpublish']
    form = ArticleExtraLangAdminForm
    save_as = True

    def publish(self, request, queryset):
        row_update = queryset.update(draft=False)
        if row_update == '1':
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')

    def unpublish(self, request, queryset):
        row_update = queryset.update(draft=True)
        if row_update == '1':
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')

    publish.short_description = 'Опубликовать'
    publish.allowed_permissions = ('change', )

    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change', )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'get_image']
    list_display_links = ['article']
    list_filter = ['article']
    fields = ['article', ('get_image', 'image')]
    readonly_fields = ['get_image']

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="75">')

    get_image.short_description = 'Изображение'


@admin.register(VideoRu)
class VideoRuAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_video', 'article']
    list_display_links = ['name_video']
    fields = ['article', 'name_video', 'video']
    inlines = [
        VideoExtraLangInline
    ]


@admin.register(VideoExtraLang)
class VideoExtraLangAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_video', 'video', 'language']
    list_display_links = ['name_video']
    list_filter = ['language']
    fields = ['video', 'language', 'name_video']


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'telephone']
    list_display_links = ['article']
    fields = ['article', 'telephone']


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'email']
    list_display_links = ['article']
    fields = ['article', 'email']


# @admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'text', 'draft']
    list_display_links = ['article']
    fields = ['article', 'parent', 'email', 'name', 'text', 'likes', 'datetime', 'draft']
    list_editable = ['draft']
    actions = ['publish', 'unpublish']
    readonly_fields = ['article', 'parent', 'email', 'name', 'text', 'likes', 'datetime']

    def publish(self, request, queryset):
        row_update = queryset.update(draft=False)
        if row_update == '1':
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')

    def unpublish(self, request, queryset):
        row_update = queryset.update(draft=True)
        if row_update == '1':
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')

    publish.short_description = 'Одобрить отзыв(ы)'
    publish.allowed_permissions = ('change', )

    unpublish.short_description = 'Скрыть отзыв(ы)'
    unpublish.allowed_permissions = ('change', )