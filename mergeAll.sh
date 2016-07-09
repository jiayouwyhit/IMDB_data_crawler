#!/bin/bash

#copy the images of each section into 'all' folder
for i in 1 2 3 4 5
do
    cp -f data/film_img/$i/*.jpg data/film_img/all/
    cp -f data/actor_small_img/$i/*.jpg data/actor_small_img/all/
    cp -f data/actor_big_img/$i/*.jpg data/actor_big_img/all/
done

#merge all the data of films, actors, and edge_characters
python mergeAll.py