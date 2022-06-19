from django.urls import path
from .views import RegionListView, SearchView, ArticleRegionView, ArticleCategoryView, ArticleRegionCategoryView,\
    ArticleDetailView # AddComment, DynamicCommentsLoad, DynamicChildCommentsLoad


urlpatterns = [
    path('', RegionListView.as_view(), name='our_land'),
    path('search', SearchView.as_view(), name='search'),
    path('region/<slug:reg>/', ArticleRegionView.as_view(), name='region'),
    path('region/<slug:reg>/<slug:art>/', ArticleDetailView.as_view(), name='article'),
    path('category/<slug:categ>/', ArticleCategoryView.as_view(), name='category'),
    path('category/<slug:reg>/<slug:categ>/', ArticleRegionCategoryView.as_view(), name='region_category'),

    # Comments
    # path('comments/', AddComment.as_view(), name='add_comment'),
    # path('load-comments/', DynamicCommentsLoad.as_view(), name='load_comments'),
    # path('load-child-comments/', DynamicChildCommentsLoad.as_view(), name='load_child_comments'),
]