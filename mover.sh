#!/bin/bash

# move the nessecary files from project directory into script dir

bind_dir=~/docker/webtop/config/movie-rename-script/ # the bind mount (host dir) of docker webtop
# copy the .env file into the script dir
cp .env $bind_dir/.env
# copy the api.sh file into the script dir
cp api.sh $bind_dir/api.sh
