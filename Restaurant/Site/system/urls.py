from django.urls import path
from . import views


urlpatterns = [
	path('', views.index, name='home'),
	path('recom', views.recom, name='recom'),
	path('post', views.post, name='post'),

]
