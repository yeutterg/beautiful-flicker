#!/usr/bin/env bash

# Starts a container and opens a bash shell or jupyter notebook within
# Parameters;
#   --jupyter or -j: starts a jupyter notebook instead of a shell

# Get params
JUPYTER=false
for arg in "$@"; do
    if [ "$arg" == "--jupyter" ] || [ "$arg" == "-j" ]
    then
        JUPYTER=true
        echo Jupyter mode
    fi
done

# Run the container in the background and get its ID
CONTAINER_ID=`docker run --rm -p 8888:8888 -d -v /$PWD:/beautiful-flicker beautiful-flicker tail -f /dev/null`
echo "Opened container $CONTAINER_ID"

if [ "$JUPYTER" = true ]; then
    # Start the jupyter server
    # The URL to run the server will be http://localhost:8888/?token= plus the token listed in the output
    docker exec -ti $CONTAINER_ID jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser /beautiful-flicker/examples
else
    # Open a bash shell inside the container
    docker exec -ti $CONTAINER_ID sh
fi