#!/bin/bash

case "$(uname -s)" in    
    CYWGWIN*|MSYS*|MINGW*)
        echo 'Windows'
        winpty docker exec -it eng_django bash    
    ;;

    *)
        echo 'Linux'
        docker exec -it eng_django bash
    ;;
esac
