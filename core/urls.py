from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns= [

    path('',views.index,name='index'),
    path('signup/',views.signup,name='signup'),
    path('like-post',views.like_post,name='like-post'),
    path('follow',views.follow,name='follow'),
    path('search',views.search,name='search'),
    path('login/',auth_views.LoginView.as_view(template_name='core/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='login'),name='logout'),
    path('settings/',views.settings,name='settings'),
    path('upload',views.upload,name='upload'),
    path('send_message/<str:username>/',views.send_message,name='send_message'),
    path('inbox/',views.inbox,name='inbox'),
    path('profile/<str:pk>/',views.profile,name='profile'),
]