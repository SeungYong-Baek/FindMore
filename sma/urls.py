from django.urls import path
from . import views

app_name = 'sma'
urlpatterns = [
        path('', views.SMAIndexView.as_view(), name='index'),
        path('list/', views.SMAListView.as_view(), name='sma_list'),
        path('list/<int:pk>/', views.SMADetailView.as_view(), name='sma_detail'),
        path('create/', views.SMACreateView.as_view(), name='sma_create'),
        path('delete/<int:pk>/', views.SMADeleteView.as_view(), name='sma_delete'),
] 
