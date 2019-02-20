from django.urls import path

from . import views


app_name = 'sistemas_colaborativos'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:usuario>/recomendar/', views.get_recomendacion, name='get_recomendacion'),
    path('<str:track>/buscar_cancion/', views.search_cancion, name='search_cancion'),
    path('<str:artist>/buscar_cancion_artista/', views.search_cancionArtista, name='buscar_cancion_artista'),
]