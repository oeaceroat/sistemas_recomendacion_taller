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

    response_data = {}

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


