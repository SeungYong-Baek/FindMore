from django.urls import path
from . import views

app_name = 'mra'
urlpatterns = [
        path('', views.MRAIndexView.as_view(), name='index'),
        path('list/', views.MRAListView.as_view(), name='mra_list'),
        path('list/<int:pk>/', views.MRADetailView.as_view(), name='mra_list_detail'),
        path('create/', views.MRACreateView.as_view(), name='mra_list_create'),
        path('delete/<int:pk>/', views.MRADeleteView.as_view(), name='mra_list_delete'),
] 
