from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('notices/', views.notices_list_view, name='notices'),
    path('notices/create/', views.create_notice_view, name='create_notice'),
    path('notices/<int:pk>/', views.notice_detail_view, name='notice_detail'),
    path('polls/', views.polls_list_view, name='polls'),
    path('polls/create/', views.create_poll_view, name='create_poll'),
    path('polls/<int:pk>/vote/', views.vote_poll_view, name='vote_poll'),
    path('forum/', views.forum_list_view, name='forum'),
    path('forum/create/', views.create_post_view, name='create_post'),
    path('forum/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('lost-found/', views.lost_found_view, name='lost_found'),
    path('lost-found/<int:pk>/claim/', views.claim_item_view, name='claim_item'),
    path('documents/', views.documents_vault_view, name='documents'),
]
