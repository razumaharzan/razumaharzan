from django.urls import path
from . import views
urlpatterns = [
    path('',views.sec_index,name='sec_index'),
    path('home/',views.home,name='home'),
    path('products',views.products,name='products'),
    path('sec_support',views.sec_support,name='sec_support'),
    path('sec_solutions',views.sec_solutions,name='sec_solutions'),
    path('edit/<pk>',views.edit_item,name="edit_item"),
    path('delete/<pk>',views.delete_item,name="delete"),
]
