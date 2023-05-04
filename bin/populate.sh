#!/bin/bash

container="eng_django"

case "$(uname -s)" in    
    CYWGWIN*|MSYS*|MINGW*)
        echo 'Windows'
        winpty docker exec -it $container python manage.py populate_questions
        winpty docker exec -it $container python manage.py populate_examples
        winpty docker exec -it $container python manage.py populate_videos
        winpty docker exec -it $container python manage.py populate_cards
        winpty docker exec -it $container python manage.py populate_users
        echo 'Done.'
    ;;

    *)
        echo 'Linux'
    ;;
esac