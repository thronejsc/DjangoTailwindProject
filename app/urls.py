from django.contrib import admin
from django.urls import path, include

from . import views
from .views import SignUpView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('wherenext/', views.where_next,name='where-next'),
    path('student', views.student_base, name='student-profile'),
    #path('editor', views.editor_base, name='editor-profile'),
    path('publisher', views.publisher_base, name='publisher-profile'),

    path('journal', views.journal_list, name='journal-list'),
    path('journal/<int:journal_id>', views.journal_view, name='journal-detail'),
    path('article/<int:article_id>', views.article_view, name='article-detail'),
    path('journal/<int:journal_id>/submit-article', views.submit_article, name='submit-article'),

    #path('editor/article-list', views.article_list, name='article-list'),
    #path('editor/article-list/pending/<int:article_id>', views.review_pending_article, name='review_article'),
    path('searchart/', views.search_articles, name='search_articles'),

    path('publisher/article-list', views.publisher_article_list, name='publisher-article-list'),
    path('publisher/article-list/accepted/<int:article_id>', views.publisher_review, name='publisher_article'),
    path('search/', views.journal_search, name='journal_search'),
    path('upload/', views.upload_document, name='upload_document'),
    path('searchdoc/', views.search_document, name='search_document'),
    path('document/<int:document_id>/', views.view_document, name='view_document'),
    path('document/<int:document_id>/comment_submit/', views.comment_submit, name='comment_submit'),
    path('documents/<int:document_id>/download/', views.download_document, name='download_document'),

]
