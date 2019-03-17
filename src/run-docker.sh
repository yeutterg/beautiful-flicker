#!/usr/bin/env bash

# Starts a container and opens a bash shell or jupyter notebook within
# Parameters;
#   --jupyter: starts a jupyter notebook instead of a shell

# Run the container in the background and get its ID
CONTAINER_ID=`docker run -p 8888:8888 -d beautiful-flicker tail -f /dev/null`
echo "Opened container $CONTAINER_ID"

if [[ "$1" == "--jupyter" ]]; then
    # Start the jupyter server
    # The URL to run the server will be http://localhost:8888/?token= plus the token listed in the output
    docker exec -ti $CONTAINER_ID jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser /examples
elif [[ -z "$1" ]]; then
    # Open a bash shell inside the container
    docker exec -ti $CONTAINER_ID sh
fi