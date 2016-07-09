#!/bin/bash

function clearAll {
    #remove all the generated data
    rm -rf data/output_imdb/*.json
    rm -rf data/output_imdb/*.csv
    rm -rf data/output_imdb/all/*.json
    rm -rf data/output_imdb/all/*.csv

    #remove all images
    for i in 1 2 3 4 5
    do
        rm -rf data/film_img/$i/*.jpg
        rm -rf data/actor_small_img/$i/*.jpg
        rm -rf data/actor_big_img/$i/*.jpg
    done

    rm -rf data/film_img/all/*.jpg
    rm -rf data/actor_small_img/all/*.jpg
    rm -rf data/actor_big_img/all/*.jpg
}

while true; do
    read -p "Do you wish to install this program?" yn
    case $yn in
        [Yy]* ) clearAll; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

