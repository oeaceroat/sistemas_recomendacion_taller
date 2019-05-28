from django.urls import path

from . import views


app_name = 'sistemas_streaming'
urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.get_movies, name='get_categories'),
    path('<str:usuario>/recomendar/', views.get_recomendacion, name='get_recomendacion'),
    path('<str:user>/<str:movie>/crear_usuario/', views.add_user, name='add_user'),

    path('<str:movie>/buscar_pelicula/', views.search_movie, name='buscar_pelicula'),
    path('<str:user>/<str:movie>/<str:rating>/calificar/', views.calificar, name='calificar'),
    path('populares/', views.populares, name='populares'),
    path('lanzamientos/', views.lanzamientos, name='lanzamientos'),
    path('<str:user>/actividad/', views.actividad, name='actividad'),
    #path('<str:traname>/<str:artname>/add_track/', views.add_track, name='add_track'),
    path('<str:usuario>/recomendar_usuario/', views.get_recomendacion_user, name='get_recomendacion_usuario'),
]

