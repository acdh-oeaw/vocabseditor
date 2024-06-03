from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'webpage'

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path('favicon\.ico', favicon_view),
    path('', views.GenericWebpageView.as_view(), name="start"),
    path('project-info/', views.project_info, name='project_info'),
    path('accounts/login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('imprint/', views.ImprintView.as_view(), name='imprint'),
    path('<slug:template>', views.GenericWebpageView.as_view(), name='staticpage'),
    path('user/<int:pk>', views.UserDetailView.as_view(), name='user_detail'),
]
