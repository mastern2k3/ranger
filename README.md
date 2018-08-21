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
python main.py start -t ./monitor -a ./archive
```

## Docker

**ranger** can also can also run in a Docker container, like this:

```sh
docker run -v $PWD:/app -v $PWD/monitor:/monitored -v $PWD/archive:/archive ranger
```
