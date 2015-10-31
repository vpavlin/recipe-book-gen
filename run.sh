#!/usr/bin/bash

IMAGE="recipe-book"
NAME="recipe-book"
FROM="/home/$USER/Dropbox/recipe-book"

exist=$(docker images -q $IMAGE)
if [ "$exist" == "" ]; then
  docker build -t $IMAGE .
fi

id=$(docker ps -q --filter=[name=$NAME])

if [ "$id" == "" ]; then
  docker rm $NAME
  docker run -d -p 5000:5000 -v $FROM:/opt/recipe-book/data -u $(id -u) --name $NAME $IMAGE
else
  docker start $id
fi

google-chrome --app=http://localhost:5000
