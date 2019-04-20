from django.urls import path

from . import views


app_name = 'sistemas_hibridos'
urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.get_categories, name='get_categories'),
    path('<str:usuario>/recomendar/', views.get_recomendacion, name='get_recomendacion'),
    path('<str:user>/<str:state>/<str:category>/crear_usuario/', views.add_user, name='add_user'),

    path('<str:restaurant>/buscar_restaurante/', views.search_restaurante, name='buscar_restaurante'),
    path('<str:user>/<str:traname>/<str:rating>/calificar/', views.calificar, name='calificar'),
    path('populares/', views.populares, name='populares'),
    path('lanzamientos/', views.lanzamientos, name='lanzamientos'),
    path('<str:user>/actividad/', views.actividad, name='actividad'),
    #path('<str:traname>/<str:artname>/add_track/', views.add_track, name='add_track'),
    path('<str:usuario>/recomendar_usuario/', views.get_recomendacion_user, name='get_recomendacion_usuario'),
]

