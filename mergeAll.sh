#!/bin/bash

#copy the images of each section into 'all' folder
# for i in 1 2 3 4 5
# do
# 	for file1 in data/film_img/$i/*.jpg; do yes|cp -rf "$file1" data/film_img/all/; done
# 	for file2 in data/actor_small_img/$i/*.jpg; do yes|cp -rf "$file2" data/actor_small_img/all/; done
# 	for file3 in data/actor_big_img/$i/*.jpg; do yes|cp -rf "$file3" data/actor_big_img/all/; done
# done

#merge all the data of films, actors, and edge_characters
python mergeAll.py