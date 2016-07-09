import io
import urllib2
import urllib
import string
import json
import re
import time
import sys
import unicodecsv as csv
# import csv
from bs4 import BeautifulSoup

film_url_header = 'http://www.imdb.com/title/tt'
actor_url_header = 'http://www.imdb.com/name/nm'
local_film_img = './data/film_img/'
local_actor_big_img = './data/actor_big_img/'
local_actor_small_img = './data/actor_small_img/'

#All the information are stored here
node_films = [] #all the info of films
node_actors = {} #all the info of actors
edge_characters = []
MAX_URL_TRY = 15


def urlOpenAndRead2GetPage(_url):
    try:
        detail_page = urllib2.urlopen(_url).read()
    except:
        print 'Error exists when reading url: ' + _url
        detail_page = 'ERROR_EXIST'
    return detail_page

def tryMaxTimesOpenUrl(_film_url):
    detail_page = 'ERROR_EXIST'
    counter = 0
    while counter < MAX_URL_TRY: #check
        counter = counter + 1
        detail_page = urlOpenAndRead2GetPage(_film_url)
        if detail_page == 'ERROR_EXIST':
            print 'Error Attemption # ' + str(counter)
            time.sleep(counter * 20)
        else:
            return detail_page
    return detail_page


def getAllFilmIdFromJSON(_file_path):
    with open(_file_path) as json_data:
        film_data = json.load(json_data)
        return film_data

def storeInfo2JsonFile( _file_path, _data):
    with open(_file_path, 'w') as f:
        f.write(json.dumps(_data))

# ID, Year, Title, rate_point, type, img_url(local)
def getMovieInfo(_movie_id, _section_id):
    print 'crawl film information of #' + _movie_id
    single_movie_info = {}
    single_movie_info['id'] = _movie_id

    film_url = film_url_header + _movie_id
    # detail_page = urllib2.urlopen(film_url).read()
    detail_page = tryMaxTimesOpenUrl(film_url)

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
    actual_local_film_img_url = local_film_img + str(_section_id) + '/' + _movie_id + '.jpg' #!!!Note: they are different!
    urllib.urlretrieve(remote_img_url, actual_local_film_img_url)
    single_movie_info['local_img_url'] = local_film_img_url

    return single_movie_info


#ID, name, gender, date of birth, place, img_url(local),
def getActorsInfo(_actor_id, _section_id):
    # print _actor_id
    single_actor_info = {}
    single_actor_info['id'] = _actor_id

    actor_url = actor_url_header + _actor_id
    # detail_page = urllib2.urlopen(actor_url).read()
    detail_page = tryMaxTimesOpenUrl(actor_url)
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
    actual_local_actor_big_img_url = local_actor_big_img + str(_section_id) + '/' + _actor_id + '.jpg'
    urllib.urlretrieve(remote_big_img_url, actual_local_actor_big_img_url)
    single_actor_info['remote_big_img_url'] = remote_big_img_url
    single_actor_info['local_big_img_url'] = local_actor_big_img_url

    return single_actor_info

def getAllActorsOfOneFilm(_film_id, _section_id):
    print 'begin to crawl actor information of film #' + _film_id
    film_url = film_url_header + _film_id + '/fullcredits?ref_=tt_cl_sm#cast'
    # detail_page = urllib2.urlopen(film_url).read()
    detail_page = tryMaxTimesOpenUrl(film_url)
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

        if remote_small_img_url.has_attr('loadlate'):
            remote_small_img_url = remote_small_img_url['loadlate']
        else:
            remote_small_img_url = remote_small_img_url['src']

        local_small_img_url = local_actor_small_img + actor_id + '.jpg'
        actual_local_small_img_url = local_actor_small_img + str(_section_id) + '/' + actor_id + '.jpg'
        urllib.urlretrieve(remote_small_img_url, actual_local_small_img_url)

        single_actor_info = getActorsInfo(actor_id, _section_id) #get the remaining info in another page
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
    # detail_page = urllib2.urlopen(film_url).read()
    detail_page = tryMaxTimesOpenUrl(film_url)
    page_info = BeautifulSoup(detail_page, "html.parser")

    actor_array = page_info.find('table', {'class': 'cast_list'}).find_all('tr', {'class': ['odd', 'even']})  # important!!! find multiple tags beneath a specific tag
    for i in range(0, len(actor_array)):
        edge_obj = {}
        each_actor = actor_array[i].find('td', {'class': 'primary_photo'})
        actor_id = each_actor.find('a')['href']
        actor_id = re.findall(r'(?<=nm)\d{7}(?=/)', actor_id, re.M | re.I)[0]

        each_character = actor_array[i].find('td', {'class': 'character'}).find('div').get_text()
        # print "character: " + each_character

        edge_obj['film_id'] = _film_id
        edge_obj['actor_id'] = actor_id

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
    #check the input arguments
    section_id = int(sys.argv[1])
    if isinstance(section_id, int) and (section_id >= 1 and section_id <= 5):
        print 'program #' + str(section_id)
    else:
        print isinstance(section_id, int)
        print 'You input the wrong section id! '
        exit(0)

    film_data = getAllFilmIdFromJSON('./data/origin_imdb/imdb.json')
    film_data_array = film_data['nodes']

    max_data_len = len(film_data_array)
    section_data_len = 1000
    if section_id == 5:
        section_data_len = max_data_len - 4000
    print 'total data length: ' + str(max_data_len) + ', section data length: ' + str(section_data_len)
    # for i in range((section_id - 1) * 1000, (section_id - 1) * 1000 + section_data_len):
    for i in range(0, 2):
        film_id = film_data_array[i]['imdbID']
        film_year = film_data_array[i]['year']
        film_title = film_data_array[i]['title']

        print 'section_id: #' + str(section_id) + ' number: #' +str(i)
        print 'film_id: ' + film_id

        #get the film information
        single_film_info = getMovieInfo(film_id, section_id)
        single_film_info['year'] = film_year
        single_film_info['title'] = film_title
        node_films.append(single_film_info)

        #update the original input imdb-data information
        film_data['nodes'][i]['local_img_url'] = single_film_info['local_img_url']

        #find actor information
        getAllActorsOfOneFilm(film_id,section_id)

        # get the edge between film and actors
        getEdgeBetweenFilmAndCast(film_id)

        # print node_films
        # print node_actors
        # print edge_characters
        print '============================finish crawling one film========================\n\n'

    #save the data to JSON file
    print '\n===========================now, let us save the data to JSON file===========\n'
    storeInfo2JsonFile('./data/output_imdb/' + str(section_id) + '_node_films.json', node_films)
    storeInfo2JsonFile('./data/output_imdb/' + str(section_id) + '_node_actors.json', node_actors)
    storeInfo2JsonFile('./data/output_imdb/' + str(section_id) + '_edge_characters.json', edge_characters)
    storeInfo2JsonFile('./data/output_imdb/' + str(section_id) + '_imdb_updated.json', film_data)

    print '\n===========================now, let us save the data to csv file===========\n'
    node_films_array = nodeFilmsTo2dArray()
    writer = csv.writer(open('./data/output_imdb/' + str(section_id) + '_node_films_array.csv', 'w'), encoding='utf-8') #encoding='utf-8'
    for row in node_films_array:
        writer.writerow(row)

    node_actors_array = nodeActorsTo2dArray()
    writer = csv.writer(open('./data/output_imdb/' + str(section_id) + '_node_actors_array.csv', 'w'), encoding='utf-8')
    for row in node_actors_array:
        writer.writerow(row)

    edge_characters_array = edgeCharactersTo2dArray()
    writer = csv.writer(open('./data/output_imdb/' + str(section_id) + '_edge_characters_array.csv', 'w'), encoding='utf-8')
    for row in edge_characters_array:
        writer.writerow(row)

    print '\n===========Congratulation!!! Enjoy the data!=====================\n'





