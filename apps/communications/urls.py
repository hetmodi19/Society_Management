from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('notices/', views.notices_list_view, name='notices'),
    path('notices/create/', views.create_notice_view, name='create_notice'),
    path('notices/<int:pk>/', views.notice_detail_view, name='notice_detail'),
    path('notices/<int:pk>/delete/', views.delete_notice_view, name='delete_notice'),
    path('polls/', views.polls_list_view, name='polls'),
    path('polls/create/', views.create_poll_view, name='create_poll'),
    path('polls/<int:pk>/vote/', views.vote_poll_view, name='vote_poll'),
    path('polls/<int:pk>/delete/', views.delete_poll_view, name='delete_poll'),
    path('forum/', views.forum_list_view, name='forum'),
    path('forum/create/', views.create_post_view, name='create_post'),
    path('forum/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('forum/<int:pk>/delete/', views.delete_post_view, name='delete_post'),
    path('forum/reply/<int:pk>/delete/', views.delete_reply_view, name='delete_reply'),
    path('lost-found/', views.lost_found_view, name='lost_found'),
    path('lost-found/<int:pk>/claim/', views.claim_item_view, name='claim_item'),
    path('lost-found/<int:pk>/delete/', views.delete_lost_found_view, name='delete_lost_found'),
    path('documents/', views.documents_vault_view, name='documents'),
    path('documents/<int:pk>/delete/', views.delete_document_view, name='delete_document'),
]
