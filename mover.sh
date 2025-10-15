#!/bin/bash

# move the nessecary files from project directory into script dir

bind_dir=~/docker/webtop/config/movie-rename-script/ # the bind mount (host dir) of docker webtop
# copy the .env file into the script dir
cp .env $bind_dir/.env
# copy api, ffp, ffs, rmads, zht2s.sh into the script dir
for file in api.sh ffp.sh ffs.sh rmads.sh zht2s.sh subprocessing.sh; do
    cp $file $bind_dir/$file
done

# Cloudflare Worker userscript (to be added manually to firefox)
export $(cat .env | xargs) && envsubst < userscript.template.js > userscript.js
cp userscript.js $bind_dir/userscript.js
