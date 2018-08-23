# ranger
A small folder watching tool that loads files into elastic search

# Usage

**ranger** acts as a command line tool, so given a folder structure that looks like this:

```
 . # Current working folder
 +
 +--> monitor # this folder will be under file watch
 |    |
 |    +--> user1 # serves user 1
 |    |
 |    +--> user2 # serves user 2
 |
 +--> archive # this folder will be used as an archive for processed files
      |
      +--> user1 # serves user 1
      |
      +--> user2 # serves user 2
```

You can run it this way:

```sh
python main.py -t ./monitor -a ./archive
```

## Docker

**ranger** can also can also run in a Docker container, like this:

```sh
# from within the repo folder
mkdir monitor
mkdir archive

docker build -t ranger .
docker run -v $PWD/monitor:/monitored -v $PWD/archive:/archive ranger
```
