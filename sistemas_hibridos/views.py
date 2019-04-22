from django.shortcuts import render
import pymongo
from pymongo import MongoClient
from django.http import JsonResponse

from surprise import SVD
from surprise import Dataset
from surprise import dump
from collections import OrderedDict
from collections import defaultdict
from itertools import islice
import os

cwd = os.getcwd()

print("Current directory : ", cwd)

client = MongoClient()
client = MongoClient('127.0.0.1', 27017)

db = client.sisrec_taller2

_, loaded_algo = dump.load('../../sistemas_recomendacion/sistema_recomendacion/sistemas_hibridos/dump_file')
n = 10

print("Model SVD", loaded_algo)


def index(request):
    context = {}
    return render(request, 'sistemas_hibridos/index_sishib.html', context)


def get_states():
    states = db.state.find().sort('state', 1)
    data = []

    for t in states:
        obj = {'id_state': t['id_state'],
               'state': t['state']}
        data.append(obj)

    return data


def get_categories():
    categories = db.category.find().sort('count', -1).limit(10)
    data = []

    for t in categories:
        obj = {'id_category': t['id_category'],
               'category': t['category']}
        data.append(obj)

    return data


def add_user(request, user, state, category):
    collection = db.user
    current_user = collection.find_one({'user_id': user})
    message = ''
    data = []
    if current_user is None:
        print('Crear nuevo usuario')
        new_user = {
            'user_id': user,
            'user_name': user,
            'id_state': state,
            'profile': [category],
            'status': 'new'
        }

        new_user = collection.insert_one(new_user)
        print(new_user.inserted_id)
        message = 'user_created'

    else:
        print('Usuario ya existe')
        message = 'user_not_created'

    response_data = {}
    response_data['message'] = message
    response_data['data'] = data
    print(message)

    return JsonResponse(response_data)


def get_recomendacion(request, usuario):
    user = db.user.find_one({'user_name': usuario})

    categories = []
    states = []
    message_2 = ''
    if user is None:
        print('Nuevo usuario')
        message = 'new_user'

        categories = get_categories()
        states = get_states()

    else:
        print('Lista de recomendación')
        message = 'Hola ' + usuario + ', descrubre los mejores restaurantes para tí'
        data = []

        ratings = user

    print('...................... ', message)

    response_data = {'message': message,
                     'categories': categories,
                     'states': states}

    print(message)

    return JsonResponse(response_data)


def search_restaurante(request, restaurant):
    collection = db.restaurant
    cursor_track = collection.find({'artname': {'$regex': '.*' + restaurant + '.*', '$options': 'i'}})

    data = []

    for t in cursor_track:
        obj = {}

        # obj['traname'] = t['traname']
        obj['artname'] = t['artname']

        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def calificar(request, user, restaurant, rating):
    # collection = db.rating
    # collection2 = db.rating_prediction
    current_user = db.user.find_one({'user_name': user})
    user_id = current_user['user_id']
    current_restaurant = db.business.find_one({"name": restaurant})
    restaurant_id = current_restaurant["business_id"]

    current_rating = db.rating.find_one({'user_id': user_id, 'business_id': restaurant_id})
    # estimated_rating = collection2.find_one({'userid': user, 'artname': artname})

    new_rating = {'user_id': user_id,
                  'business_id': restaurant_id,
                  'stars': int(rating),
                  'client_state': current_user['id_state'],
                  'city': current_restaurant['city'],
                  'state': current_restaurant['state']
                  }

    if current_rating is None:

        r = db.rating.insert_one(new_rating)
        id = str(r.inserted_id)
        print('Nuevo rating: ' + id)
    else:
        deleted_rating = db.rating.delete_many({'user_id': user_id, 'business_id': restaurant_id})
        r = db.rating.insert_one(new_rating)
        id = str(r.inserted_id)
        print('Rating actualizado: ' + id)

    message = user + ' has calificado con  ' + rating + ' puntos a ' + current_restaurant['name']

    response_data = {}
    response_data['message'] = message
    print(message)
    return JsonResponse(response_data)


def populares(request):

    top = db.rating.aggregate([
        {'$group': {
            "_id": {
                'business_id': '$business_id',
                #      'traname': '$traname'
            },
            'rating_count': {'$sum': 1},
            'rating_avg': {'$avg': '$stars'}
        }},
        {"$match": {"rating_avg": {"$gte": 4.0}, "rating_count": {"$gte": 10}}},
        {'$sort': {'rating_count': -1, }},
        {'$limit': 10}
    ])

    data = []

    for t in top:
        item_id = t['_id']['business_id']
        item = db.business.find_one({'business_id': item_id})

        obj = {'name': item['name'],
               'categories': item['categories'],
               'address': item['address'],
               'state': item['state'],
               'city': item['city'],
               'rating_count': float("{0:.2f}".format(t['rating_count'])),
               'rating_avg': float("{0:.2f}".format(t['rating_avg']))
               }

        data.append(obj)


    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def actividad(request, user):
    current_user = db.user.find_one({'user_name': user})
    user_id = current_user['user_id']
    user_ratings = db.rating.find({'user_id': user_id}).sort([('stars', pymongo.DESCENDING), ('_id', pymongo.DESCENDING)]).limit(50)

    #sort([("field1", pymongo.ASCENDING), ("field2", pymongo.DESCENDING)])

    data = []

    for t in user_ratings:
        item_id = t['business_id']
        item = db.business.find_one({'business_id': item_id})
        obj = {'name': item['name'],
               'categories': item['categories'],
               'address': item['address'],
               'state': item['state'],
               'city': item['city'],
               # 'hours': item['hours'],
               'rating': float("{0:.2f}".format(t['stars']))
               }
        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def lanzamientos(request):

    new_restaurants = db.business.find().sort('_id', -1).limit(15)

    data = []

    for t in new_restaurants:

        item_id = t['business_id']
        item = db.business.find_one({'business_id': item_id})

        obj = {'name': item['name'],
               'categories': item['categories'],
               'address': item['address'],
               'state': item['state'],
               'city': item['city']
               }

        data.append(obj)

    response_data = {}
    response_data["data"] = data

    print(response_data)
    return JsonResponse(response_data)


def add_track(request, traname, artname):
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
    current_user = db.user.find_one({'user_name': usuario})
    print("usuario activo: ", current_user)
    profile = current_user['profile']
    user_state = current_user["id_state"]

    #profile_str =

    try:
        status = current_user['status']
    except:
        status = ''

    data = []
    list_rec_1 = []
    list_rec_2 = []

    if status == 'new':
        print("Usuario no entrenado con SVD")
        message = "new_user"

        list_1 = db.new_user_list.find_one({"$and": [{"state": user_state},
                                                     {"category_list_1": profile[0]}]})

        print("lista usuario nuevo: ", list_1)

        l1 = list_1['list_1']
        l1_stars = list_1['stars_list_1']

        for i, rating in zip(l1, l1_stars):

            item = db.business.find_one({"business_id": i})

            obj = {'name': item['name'],
                   'categories': item['categories'],
                   'address': item['address'],
                   'state': item['state'],
                   'city': item['city'],
                   # 'hours': item['hours'],
                   'rating': rating
                   }
            list_rec_1.append(obj)

        list_2 = db.new_user_list.find_one({"$and": [{"state": user_state},
                                                     {"category_list_2": profile[0]}]})

        l2 = list_1['list_2']
        l2_stars = list_1['stars_list_2']

        for i, rating in zip(l2, l2_stars):

            item = db.business.find_one({"business_id": i})

            obj = {'name': item['name'],
                   'categories': item['categories'],
                   'address': item['address'],
                   'state': item['state'],
                   'city': item['city'],
                   # 'hours': item['hours'],
                   'rating': rating
                   }
            list_rec_2.append(obj)

    else:
        message = "old_user"
        print("Usuario pre-entrenado con SVD")
        user_id = current_user["user_id"]

        list_1 = db.old_user_list.find_one({"user_id": user_id})

        if list_1 is not None:

            l1 = list_1['list_1']
            l1_stars = list_1['stars_list_1']

            for i, rating in zip(l1, l1_stars):

                item = db.business.find_one({"business_id": i})

                obj = {'name': item['name'],
                       'categories': item['categories'],
                       'address': item['address'],
                       'state': item['state'],
                       'city': item['city'],
                       # 'hours': item['hours'],
                       'rating': rating
                       }
                list_rec_1.append(obj)




        rated_items = db.rating.find({'user_id': user_id}).distinct('business_id')
        unrated_items = db.rating.find({"$and": [{'business_id': {'$nin': rated_items}},
                                                 {'state': user_state}]}).distinct('business_id')

        #unrated_items = db.rating.find({'business_id': {'$nin': rated_items}}).distinct('business_id')

        # unrated_items = db.rating.find({'user_id': {"$ne": user_id}}).distinct("business_id")
        print(len(rated_items), " items calificados")
        print(len(unrated_items), " items no calificados")

        top_n = get_top_n_SVD(loaded_algo, user_id, unrated_items, n)

        for key, value in top_n.items():
            item = db.business.find_one({'business_id': key})
            obj = {'name': item['name'],
                   'categories': item['categories'],
                   'address': item['address'],
                   'state': item['state'],
                   'city': item['city'],
                   # 'hours': item['hours'],
                   'rating': float("{0:.2f}".format(value))
                   }

            print(key, value)
            data.append(obj)

    # collection = db.rating_prediction
    # user_recomendations = collection.find({'userid': usuario}).sort('est_rating', -1).limit(20)

    # data = []
    # for t in user_recomendations:
    #   obj = {}
    #  obj['artname'] = t['artname']
    #  obj['est_rating'] = t['est_rating']
    #  data.append(obj)

    response_data = {}
    response_data["data"] = data
    response_data["list_1"] = list_rec_1
    response_data["list_2"] = list_rec_2
    response_data["message"] = message
    response_data["profile"] = profile
    print(response_data)
    return JsonResponse(response_data)


def get_top_n_SVD(model, user_id, unrated, n):
    user_ratings = defaultdict()
    for i in unrated:
        user_ratings[i] = loaded_algo.predict(uid=user_id, iid=i).est

    user_ratings = OrderedDict(sorted(user_ratings.items(), key=lambda t: t[1], reverse=True))
    top_n = dict(list(islice(user_ratings.items(), n)))
    top_n = OrderedDict(sorted(top_n.items(), key=lambda t: t[1], reverse=True))

    return top_n
