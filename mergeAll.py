import io
import urllib2
import urllib
import string
import json
import re
import time
import sys
import unicodecsv as csv

output_imdb_path = './data/output_imdb/'
max_section = 5

node_films = [] #all the info of films
node_actors = {} #all the info of actors
edge_characters = []

def getAllInfoFromJSON(_file_path):
    with open(_file_path) as json_data:
        film_data = json.load(json_data)
        return film_data

def storeInfo2JsonFile( _file_path, _data):
    with open(_file_path, 'w') as f:
        f.write(json.dumps(_data))


def nodeFilmsTo2dArray():
    dim1 = len(node_films)
    node_films_array = []
    for i in range(0, dim1):
        each_row = []
        for key in node_films[i]:
            each_row.append(node_films[i][key])
        node_films_array.append(each_row)

    return node_films_array

def nodeActorsTo2dArray():
    node_actors_array = []
    for key1 in node_actors:
        each_row = []
        for key2 in node_actors[key1]:
            each_row.append(node_actors[key1][key2])
        node_actors_array.append(each_row)
    return node_actors_array

def edgeCharactersTo2dArray():
    dim1 = len(edge_characters)
    edge_characters_array = []
    for i in range(0, dim1):
        each_row = []
        for key in edge_characters[i]:
            each_row.append(edge_characters[i][key])
        edge_characters_array.append(each_row)
    return edge_characters_array



if __name__ == "__main__":
    film_id_set = set()
    edge_characters_id_set = set()
    for i in range(0, max_section):
        #film information
        film_tmp1 = getAllInfoFromJSON( output_imdb_path + str(i+1) + '_node_films.json')
        # film_tmp = map(dict, set(tuple(id.items()) for id in film_tmp1)) #there are duplicated values, make the value unique
        # node_films.extend(film_tmp)
        for j in range(0,len(film_tmp1)):
            id_tmp = film_tmp1[j]['id']
            flag  = id_tmp in film_id_set
            if flag == False:
                node_films.append(film_tmp1[j])

        #actor_information
        actor_tmp = getAllInfoFromJSON(output_imdb_path + str(i+1) + '_node_actors.json')
        for actor_id in actor_tmp:
            if (node_actors.has_key(actor_id)):
                node_actors[actor_id]['film_list'].extend(actor_tmp[actor_id]['film_list'])
            else:
                node_actors[actor_id] = actor_tmp[actor_id]

        #edge_characters
        character_tmp1 = getAllInfoFromJSON(output_imdb_path + str(i+1) + '_edge_characters.json')
        # character_tmp = map(dict, set(tuple(film_id.items()) for film_id in character_tmp1)) #there are duplicated values, make the value unique
        # edge_characters.extend(character_tmp)
        for j in range(0,len(character_tmp1)):
            edge_character_tmp = character_tmp1[j]['film_id'] + character_tmp1[j]['actor_id']
            flag  = edge_character_tmp in edge_characters_id_set
            if flag == False:
                edge_characters.append(character_tmp1[j])
        

    #save information to json
    storeInfo2JsonFile(output_imdb_path + 'all/node_films.json', node_films)
    storeInfo2JsonFile(output_imdb_path + 'all/node_actors.json', node_actors)
    storeInfo2JsonFile(output_imdb_path + 'all/edge_characters.json', edge_characters)


    #save information to csv
    node_films_array = nodeFilmsTo2dArray()
    writer = csv.writer(open(output_imdb_path + 'all/node_films_array.csv', 'w'), encoding='utf-8')  # encoding='utf-8'
    for row in node_films_array:
        writer.writerow(row)

    node_actors_array = nodeActorsTo2dArray()
    writer = csv.writer(open(output_imdb_path + 'all/node_actors_array.csv', 'w'), encoding='utf-8')
    for row in node_actors_array:
        writer.writerow(row)

    edge_characters_array = edgeCharactersTo2dArray()
    writer = csv.writer(open(output_imdb_path + 'all/edge_characters_array.csv', 'w'), encoding='utf-8')
    for row in edge_characters_array:
        writer.writerow(row)

    print "total films: " + str(len(node_films))
    print "total actors: " + str(len(node_actors_array))
    print "total charactor-film edges: " + str(len(edge_characters))

    print '===============================Job is done!==========================\n\n'