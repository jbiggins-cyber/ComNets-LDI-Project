#!/bin/sh
HELP_TEXT="Shell script to manage docker images.
Usage for building/running:
    ./docker_tools.sh [build|run] [client|server]
To remove the network:  
   ./docker_tools.sh cleanup
"

function check_docker_image() {
    docker inspect --type=image "$1" > /dev/null 2>&1
}

# build 
if [ "$1" == "build" ]; then
    if [ "$2" == "client" ]; then
        docker build -t rdt-client --target client .
    elif [ "$2" == "server" ]; then
        docker build -t rdt-server --target server .
    fi

# run
elif [ "$1" == "run" ]; then

    # ensure we have a network up
    docker network inspect my-network >/dev/null || docker network create my-network >/dev/null

    # if images haven't been built yet, build them. Then, run the container
    if [ "$2" == "client" ]; then
        check_docker_image rdt-client || docker build -t rdt-client --target client .
        docker run --rm -it --network my-network --name client-ip rdt-client
    elif [ "$2" == "server" ]; then
        check_docker_image rdt-server || docker build -t rdt-server --target server .
        # the name server-ip lets us communicate to the container with that as the IP
        docker run --rm -it --network my-network --name server-ip rdt-server
    fi

elif [ "$1" == "cleanup" ]; then
    docker network prune

else
    echo "$HELP_TEXT"
fi
