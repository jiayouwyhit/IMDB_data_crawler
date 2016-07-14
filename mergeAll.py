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

    keys = ['id','title','year','rate_point','local_img_url','remote_img_url']
    node_films_array.append(keys);
    for i in range(0, dim1):
        each_row = []
        for j in range(0, len(keys)):
            each_row.append(node_films[i][keys[j]])
        node_films_array.append(each_row)
    return node_films_array

    # each_row = []
    # for key in node_films[0]:
    #     each_row.append(key)
    # node_films_array.append(each_row) #save the keys to the first row
    #
    # for i in range(0, dim1):
    #     each_row = []
    #     for key in node_films[i]:
    #         each_row.append(node_films[i][key])
    #     node_films_array.append(each_row)
    # return node_films_array

def nodeActorsTo2dArray():
    node_actors_array = []

    keys = ['id','name','gender', 'date_of_birth', 'birth_place','remote_small_img_url','remote_big_img_url','local_small_img_url','local_big_img_url']
    node_actors_array.append(keys)
    for key1 in node_actors:
        each_row = []
        for i in range(0, len(keys)):
            each_row.append(node_actors[key1][keys[i]])
        node_actors_array.append(each_row)
    return node_actors_array

    # counter = 0
    # for key1 in node_actors:
    #     counter += 1
    #     each_row = []
    #     keys_row = []#store all the keys
    #     for key2 in node_actors[key1]:
    #         each_row.append(node_actors[key1][key2])
    #         keys_row.append(key2)
    #
    #     if(counter == 1):
    #         node_actors_array.append(keys_row)
    #     node_actors_array.append(each_row)
    # return node_actors_array

def edgeCharactersTo2dArray():
    dim1 = len(edge_characters)
    edge_characters_array = []

    keys = ['actor_id', 'film_id', 'character']
    for i in range(0, dim1):
        each_row = []
        for j in range(0,len(keys)):
            each_row.append(edge_characters[i][keys[j]])
        edge_characters_array.append(each_row)
    return edge_characters_array

    # each_row = []
    # for key in edge_characters[0]:
    #     each_row.append(key)
    # edge_characters_array.append(each_row)
    #
    # for i in range(0, dim1):
    #     each_row = []
    #     for key in edge_characters[i]:
    #         each_row.append(edge_characters[i][key])
    #     edge_characters_array.append(each_row)
    # return edge_characters_array



if __name__ == "__main__":
    film_id_set = set()
    edge_characters_id_set = set()
    for i in range(0, max_section):
        #film information
        film_tmp1 = getAllInfoFromJSON( output_imdb_path + str(i+1) + '_node_films.json')
        # film_tmp = map(dict, set(tuple(id.items()) for id in film_tmp1)) #there are duplicated values, make the value unique
        # node_films.extend(film_tmp)
        for j in range(0,len(film_tmp1)):
            id_tmp = 'tt' + film_tmp1[j]['id']
            film_tmp1[j]['id'] = id_tmp # add the "tt" flag to the id of film

            film_tmp1[j].pop('type',None) #delete this attribute

            flag  = id_tmp in film_id_set
            if flag == False:
                node_films.append(film_tmp1[j])
                film_id_set.add(id_tmp) #add the id into set


        #actor_information
        actor_tmp = getAllInfoFromJSON(output_imdb_path + str(i+1) + '_node_actors.json')
        for actor_id in actor_tmp:
            id_tmp = 'nm' + actor_id # add "nm" flag to the id of each actor
            # film_lens = len(actor_tmp[actor_id]['film_list'])
            # for k in range(0, film_lens):
            #     actor_tmp[actor_id]['film_list'][k] = 'tt' + actor_tmp[actor_id]['film_list'][k] 
            # if (node_actors.has_key(id_tmp)):
            #     node_actors[id_tmp]['film_list'].extend(actor_tmp[actor_id]['film_list'])
            # else:
            #     node_actors[id_tmp] = actor_tmp[actor_id]
            actor_tmp[actor_id].pop('film_list',None)
            actor_tmp[actor_id].pop('job_title',None)
            actor_tmp[actor_id]['id'] = id_tmp
            if (node_actors.has_key(id_tmp)):
                pass
            else:
                node_actors[id_tmp] = actor_tmp[actor_id]

        #edge_characters
        character_tmp1 = getAllInfoFromJSON(output_imdb_path + str(i+1) + '_edge_characters.json')
        for j in range(0,len(character_tmp1)):
            edge_character_tmp = character_tmp1[j]['film_id'] + character_tmp1[j]['actor_id']
            flag  = edge_character_tmp in edge_characters_id_set
            if flag == False:
                character_tmp1[j]['film_id'] = 'tt' + character_tmp1[j]['film_id']
                character_tmp1[j]['actor_id'] = 'nm' + character_tmp1[j]['actor_id']
                edge_characters.append(character_tmp1[j])
                edge_characters_id_set.add(edge_character_tmp)
        

    #save information to json
    storeInfo2JsonFile(output_imdb_path + 'all/node_films.json', node_films)
    storeInfo2JsonFile(output_imdb_path + 'all/node_actors.json', node_actors)
    storeInfo2JsonFile(output_imdb_path + 'all/edge_characters.json', edge_characters)


    #save information to csv
    node_films_array = nodeFilmsTo2dArray()
    writer = csv.writer(open(output_imdb_path + 'all/node_films.csv', 'w'), encoding='utf-8')  # encoding='utf-8'
    for row in node_films_array:
        writer.writerow(row)

    node_actors_array = nodeActorsTo2dArray()
    writer = csv.writer(open(output_imdb_path + 'all/node_actors.csv', 'w'), encoding='utf-8')
    for row in node_actors_array:
        writer.writerow(row)

    edge_characters_array = edgeCharactersTo2dArray()
    writer = csv.writer(open(output_imdb_path + 'all/edge_characters.csv', 'w'), encoding='utf-8')
    for row in edge_characters_array:
        writer.writerow(row)

    print "total films: " + str(len(node_films))
    print "total actors: " + str(len(node_actors_array))
    print "total charactor-film edges: " + str(len(edge_characters))

    print '===============================Job is done!==========================\n\n'