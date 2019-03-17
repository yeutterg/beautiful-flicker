# Docker Installation and Use

With Docker installed, clone the repository, and from the project root, run:

```console
docker build --tag beautiful-flicker .
```

To run the project and access the command line, run:

```console
sh src/run-docker.sh
```

To load the Jupyter Notebook server, run:

```console
sh src/run-docker.sh --jupyter
```

You will be able to access the Jupyter server at http://localhost:8888/ . The token will be provided by Jupyter from the command line.

To see running Docker containers:

```console
docker ps
```

To kill the Docker session:

```console
docker kill CONTAINER_ID
```