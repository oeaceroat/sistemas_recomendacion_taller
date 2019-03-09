from django.shortcuts import render
import pymongo
from pymongo import MongoClient
from django.http import JsonResponse
import json

client = MongoClient()
client = MongoClient('127.0.0.1', 27017)


db = client.sisrec_taller1


def index(request):

    context = {}
    return render(request, 'sistemas_colaborativos/index_siscol.html', context)


def get_recomendacion(request,usuario):

    collection = db.user
    user = collection.find_one({'user_id':usuario})

    if user is None:
        print('Nuevo usuario')
    else:
        print('Lista de recomendación')

    message = 'Hola ' + usuario + ', encuentra a tus artistas favoritos y descubre muchos más'

    response_data = {}
    response_data['message'] = message
    print(message)

    return JsonResponse(response_data)


def search_cancion(request, track):

    collection = db.track
    cursor_track = collection.find({'traname': {'$regex': '.*' + track + '.*', '$options': 'i'}})

    obj = {}
    data = []

    for t in cursor_track:

        obj = {}
        obj['traname'] = t['traname']
        obj['artname'] = t['artname']

        data.append(obj)

    response_data = {}
    response_data["data"] = data
    print (response_data)
    return JsonResponse(response_data)


def search_cancionArtista(request, artist):

    collection = db.track
    cursor_track = collection.find({'artname': {'$regex': '.*' + artist + '.*', '$options': 'i'}})


    data = []

    for t in cursor_track:

        obj = {}

        #obj['traname'] = t['traname']
        obj['artname'] = t['artname']

        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print (response_data)
    return JsonResponse(response_data)


def calificar(request,user,traname,artname,rating):

    collection = db.rating
    collection2 = db.rating_prediction

    current_rating = collection.find_one({'userid': user, 'artname': artname})
    estimated_rating = collection2.find_one({'userid': user, 'artname': artname})

    new_rating = {'userid': user,
                  'artname': artname,
                  #'traname': traname,
                  'blend_rank': int(rating)
                  }

    if current_rating is None:
        if estimated_rating is not None:
            deleted_rating = collection2.delete_many({'userid': user, 'artname': artname})

        r = collection.insert_one(new_rating)
        id = str( r.inserted_id)
        print('Nuevo rating: ' + id)



    else:

        if estimated_rating is not None:
            deleted_rating = collection2.delete_many({'userid': user, 'artname': artname})

        deleted_rating = collection.delete_many({'userid': user, 'artname': artname})

        r = collection.insert_one(new_rating)
        id = str(r.inserted_id)
        print('Rating actualizado: ' + id)

    message = user + ' has calificado con  ' + rating + ' puntos a ' + artname

    response_data = {}
    response_data['message'] = message
    print(message)
    return JsonResponse(response_data)


def populares(request):

    collection = db.rating

    top = collection.aggregate([
        {'$group': {
            "_id": {
                'artname': '$artname',
          #      'traname': '$traname'
            },
            'rating_count': {'$sum': 1},
            'rating_avg': {'$avg': '$blend_rank'}
        }},
        {"$match": {"rating_avg": {"$gte":4.0}, "rating_count": {"$gte":10} }},
        {'$sort': {'rating_count': -1, }},
        {'$limit': 20}
    ])

    data = []

    for t in top:
        obj = {}
   #     obj['traname'] = t['_id']['traname']
        obj['artname'] = t['_id']['artname']
        obj['rating_count'] = t['rating_count']
        obj['rating_avg'] = t['rating_avg']
        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def actividad(request, user):

    collection = db.rating
    user_ratings = collection.find({'userid': user}).sort('_id', -1).limit(500)

    data = []

    for t in user_ratings:
        obj = {}
  #      obj['traname'] = t['traname']
        obj['artname'] = t['artname']
        obj['blend_rank'] = t['blend_rank']
        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def lanzamientos(request):
    collection = db.track
    new_tracks = collection.find().sort('_id', -1).limit(50)

    data = []

    for t in new_tracks:
        obj = {}
     #   obj['traname'] = t['traname']
        obj['artname'] = t['artname']
        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def add_track(request,traname,artname):

    collection = db.track

    artista = collection.find_one({'artname': artname})

    if artista is None:

        new_track = {'artname': artname
                    }
        t = collection.insert_one(new_track)
        id = str(t.inserted_id)
        print('Nuevo raitng: ' + id)

        message = 'Se ha creado el artista ' + artname + ' exitosamente'

    else:
        message = 'El artista ' + artname + ' ya existe en el sistema'

    response_data = {}
    response_data['message'] = message
    print(message)

    return JsonResponse(response_data)


def get_recomendacion_user(reuest, usuario):

    collection = db.rating_prediction
    user_recomendations = collection.find({'userid': usuario}).sort('est_rating', -1).limit(20)

    data = []
    for t in user_recomendations:
        obj = {}
        obj['artname'] = t['artname']
        obj['est_rating'] = t['est_rating']
        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


