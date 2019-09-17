from django.urls import path
from . import views

app_name = 'bah'
urlpatterns = [
        path('', views.BAHIndexView.as_view(), name='index'),
        path('list/', views.BAHListView.as_view(), name='bah_list'),
        path('list/<int:pk>/', views.BAHDetailView.as_view(), name='bah_detail'),
        path('create/', views.BAHCreateView.as_view(), name='bah_create'),
        path('delete/<int:pk>/', views.BAHDeleteView.as_view(), name='bah_delete'),
] 
