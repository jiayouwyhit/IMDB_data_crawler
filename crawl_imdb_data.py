import io
import urllib2
import urllib
import string
import json
import re
# import csv
import unicodecsv as csv
from bs4 import BeautifulSoup

film_url_header = 'http://www.imdb.com/title/tt'
actor_url_header = 'http://www.imdb.com/name/nm'
local_film_img = '../data/film_img/'
local_actor_big_img = '../data/actor_big_img/'
local_actor_small_img = '../data/actor_small_img/'

#All the information are stored here
node_films = [] #all the info of films
node_actors = {} #all the info of actors
edge_characters = []

def getAllFilmIdFromJSON(_file_path):
    with open(_file_path) as json_data:
        film_data = json.load(json_data)
        return film_data

def storeInfo2JsonFile( _file_path, _data):
    with open(_file_path, 'w') as f:
        f.write(json.dumps(_data))

# ID, Year, Title, rate_point, type, img_url(local)
def getMovieInfo(_movie_id):
    print 'crawl film information of #' + _movie_id
    single_movie_info = {}
    single_movie_info['id'] = _movie_id

    film_url = film_url_header + _movie_id
    detail_page = urllib2.urlopen(film_url)
    page_info = BeautifulSoup(detail_page, "html.parser")
    single_movie_info['rate_point'] = page_info.find('span',{'itemprop':'ratingValue'}).text

    single_movie_info['type'] = []
    type_array = page_info.find_all('span',{'itemprop':"genre"})
    for i in range(0, len(type_array)):
        tmp = type_array[i].get_text()
        single_movie_info['type'].append(tmp)

    remote_img_url = page_info.find('img', {'itemprop':'image'})['src']
    single_movie_info['remote_img_url'] = remote_img_url
    local_film_img_url = local_film_img + _movie_id + '.jpg'
    urllib.urlretrieve(remote_img_url, local_film_img_url)
    single_movie_info['local_img_url'] = local_film_img_url

    return single_movie_info


#ID, name, gender, date of birth, place, img_url(local),
def getActorsInfo(_actor_id):
    # print _actor_id
    single_actor_info = {}
    single_actor_info['id'] = _actor_id

    actor_url = actor_url_header + _actor_id
    detail_page = urllib2.urlopen(actor_url)
    page_info = BeautifulSoup(detail_page, 'html.parser')

    single_actor_info['name'] = page_info.find('span',{'itemprop':"name"}).get_text()

    single_actor_info['job_title'] = []
    single_actor_info['gender'] = 'unknown'
    job_title_array = page_info.find_all('span',{'itemprop':"jobTitle"})
    for i in range(0, len(job_title_array)):
        tmp = job_title_array[i].get_text().replace('\n','')
        single_actor_info['job_title'].append(tmp)
        if tmp == 'Actor':
            single_actor_info['gender'] = 'male'
        elif tmp == 'Actress':
            single_actor_info['gender'] = 'female'

    date_of_birth = page_info.find('time', {'itemprop': "birthDate"})
    if date_of_birth is None:
        single_actor_info['date_of_birth'] = 'unknown'
    else:
        single_actor_info['date_of_birth'] = page_info.find('time', {'itemprop': "birthDate"})['datetime']

    birth_place = page_info.find('div', {'id':'name-born-info'})
    if birth_place is None:
        single_actor_info['birth_place'] = 'unknown'
    else:
        birth_place = page_info.find('div', {'id':'name-born-info'}).find_all('a', recursive=False)
        if birth_place is None or len(birth_place) == 0:
            single_actor_info['birth_place'] = 'unknown'
        else:
            # print birth_place
            single_actor_info['birth_place'] = page_info.find('div', {'id':'name-born-info'}).find_all('a', recursive=False)[0].get_text()

    remote_big_img_url = page_info.find('img', {'id':'name-poster'})
    if remote_big_img_url is None:
        remote_big_img_url = page_info.find('td', {'id': 'overview-top'}).find('img', {'class': 'no-pic-image'})['src']
    else:
        remote_big_img_url = page_info.find('img', {'id':'name-poster'})['src']

    # print remote_big_img_url

    local_actor_big_img_url = local_actor_big_img + _actor_id + '.jpg'
    urllib.urlretrieve(remote_big_img_url, local_actor_big_img_url)
    single_actor_info['remote_big_img_url'] = remote_big_img_url
    single_actor_info['local_big_img_url'] = local_actor_big_img_url

    return single_actor_info

def getAllActorsOfOneFilm(_film_id):
    print 'begin to crawl actor information of film #' + _film_id
    film_url = film_url_header + _film_id + '/fullcredits?ref_=tt_cl_sm#cast'
    detail_page = urllib2.urlopen(film_url)
    page_info = BeautifulSoup(detail_page, "html.parser")

    actor_array = page_info.find('table', {'class': 'cast_list'}).find_all('tr', {'class': ['odd', 'even']}) #important!!! find multiple tags beneath a specific tag
    for i in range(0, len(actor_array)):
        each_actor = actor_array[i].find('td', {'class': 'primary_photo'})
        actor_id = each_actor.find('a')['href']
        actor_id = re.findall(r'(?<=nm)\d{7}(?=/)', actor_id,re.M|re.I)[0]

        #we have updated this actor's basic information
        if(node_actors.has_key(actor_id)):
            node_actors[actor_id]['film_list'].append(_film_id)
            continue
        #we have not updated this actor's basic information before
        remote_small_img_url = each_actor.find('a').find('img')
        # print each_actor
        # print '=====\n\n'
        # print each_actor.find('a')
        # print '=====\n\n'
        # print each_actor.find('a').find('img')
        # print '=====\n\n'

        if remote_small_img_url.has_attr('loadlate'):
            remote_small_img_url = remote_small_img_url['loadlate']
        else:
            remote_small_img_url = remote_small_img_url['src']

        local_small_img_url = local_actor_small_img + actor_id + '.jpg'
        urllib.urlretrieve(remote_small_img_url, local_small_img_url)

        single_actor_info = getActorsInfo(actor_id) #get the remaining info in another page
        single_actor_info['remote_small_img_url'] = remote_small_img_url
        single_actor_info['local_small_img_url'] = local_small_img_url

        single_actor_info['film_list'] = []
        single_actor_info['film_list'].append(_film_id)

        node_actors[actor_id] = single_actor_info

        # print actor_id
        # print '$$$$$$$$$$$$$$$$$$$$$$\n'

    # print actor_array
    # print '=======================\n'

def getEdgeBetweenFilmAndCast(_film_id):
    film_url = film_url_header + _film_id + '/fullcredits?ref_=tt_cl_sm#cast'
    detail_page = urllib2.urlopen(film_url)
    page_info = BeautifulSoup(detail_page, "html.parser")

    actor_array = page_info.find('table', {'class': 'cast_list'}).find_all('tr', {'class': ['odd', 'even']})  # important!!! find multiple tags beneath a specific tag
    for i in range(0, len(actor_array)):
        print "film_id: " + _film_id
        edge_obj = {}
        each_actor = actor_array[i].find('td', {'class': 'primary_photo'})
        actor_id = each_actor.find('a')['href']
        actor_id = re.findall(r'(?<=nm)\d{7}(?=/)', actor_id, re.M | re.I)[0]

        each_character = actor_array[i].find('td', {'class': 'character'}).find('div').get_text()
        # print "character: " + each_character

        edge_obj['film_id'] = _film_id
        edge_obj['actor_id'] = actor_id
        print "crawling author # " + actor_id

        # each_character = re.findall(r'\b\S+\b', each_character, re.M | re.I)
        each_character = re.findall(r'\S+', each_character, re.M | re.I)
        character = ''
        for i in range(0, len(each_character)):
            if i == 0:
                character += each_character[i]
            else:
                character += (' ' + each_character[i])

        edge_obj['character'] = character

        edge_characters.append(edge_obj)

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

if __name__ =="__main__":
    film_data = getAllFilmIdFromJSON('../data/imdb.json')
    film_data_array = film_data['nodes']

    # for i in range(0, len(film_data_array)):
    for i in range(0, 1):
        film_id = film_data_array[i]['imdbID']
        film_year = film_data_array[i]['year']
        film_title = film_data_array[i]['title']

        print 'film_id: ' + film_id

        #get the film information
        single_film_info = getMovieInfo(film_id)
        single_film_info['year'] = film_year
        single_film_info['title'] = film_title
        node_films.append(single_film_info)

        #update the original input imdb-data information
        film_data['nodes'][i]['local_img_url'] = single_film_info['local_img_url']

        #find actor information
        getAllActorsOfOneFilm(film_id)

        # get the edge between film and actors
        getEdgeBetweenFilmAndCast(film_id)

        # print node_films
        # print node_actors
        # print edge_characters
        print '============================finish crawling one film========================\n\n'

    #save the data to JSON file
    print '\n===========================now, let us save the data to JSON file===========\n'
    storeInfo2JsonFile('../data/node_films.json', node_films)
    storeInfo2JsonFile('../data/node_actors.json', node_actors)
    storeInfo2JsonFile('../data/edge_characters.json', edge_characters)
    storeInfo2JsonFile('../data/imdb_updated.json', film_data)

    print '\n===========================now, let us save the data to csv file===========\n'
    node_films_array = nodeFilmsTo2dArray()
    writer = csv.writer(open('../data/node_films_array.csv', 'w'), encoding='utf-8') #encoding='utf-8'
    for row in node_films_array:
        writer.writerow(row)

    node_actors_array = nodeActorsTo2dArray()
    writer = csv.writer(open('../data/node_actors_array.csv', 'w'), encoding='utf-8')
    for row in node_actors_array:
        writer.writerow(row)

    edge_characters_array = edgeCharactersTo2dArray()
    writer = csv.writer(open('../data/edge_characters_array.csv', 'w'), encoding='utf-8')
    for row in edge_characters_array:
        writer.writerow(row)

    print '\n===========Congratulation!!! Enjoy the data!=====================\n'





