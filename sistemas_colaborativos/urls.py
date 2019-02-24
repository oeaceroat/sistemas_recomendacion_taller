from django.urls import path

from . import views


app_name = 'sistemas_colaborativos'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:usuario>/recomendar/', views.get_recomendacion, name='get_recomendacion'),
    path('<str:track>/buscar_cancion/', views.search_cancion, name='search_cancion'),
    path('<str:artist>/buscar_cancion_artista/', views.search_cancionArtista, name='buscar_cancion_artista'),
    path('<str:user>/<str:traname>/<str:artname>/<str:rating>/calificar/', views.calificar, name='calificar'),
    path('populares/', views.populares, name='populares'),
    path('lanzamientos/', views.lanzamientos, name='lanzamientos'),
    path('<str:user>/actividad/', views.actividad, name='actividad'),
    path('<str:traname>/<str:artname>/add_track/', views.add_track, name='add_track'),
]