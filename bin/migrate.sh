#!/bin/bash

container="eng_django"

case "$(uname -s)" in    
    CYWGWIN*|MSYS*|MINGW*)
        echo 'Windows'

        echo 'Making migrations...'
        winpty docker exec  -it $container python manage.py makemigrations
        echo 'Migrating...'
        winpty docker exec  -it $container python manage.py migrate
        echo 'Done.'
    ;;

    *)
        echo 'Linux'
    ;;
esac