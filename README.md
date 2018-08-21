# fum-persist
persistence tools for fum

persistence protocol:
--------------------

0.  Setup of the serverless function:  Executed with the following environment variables set:
  -  `FUM_NODE_ID`: node number (usually 0..7)
  -  `FUM_NODE_IP`: IP address or host of this node
  -  `FUM_NODE_PORT`: IP port that the serverless function will listen on.
  -  `FUM_HOST_IP`: IP address or host of the FUM server
  -  `FUM_HOST_PORT`: IP port that the FUM server will listen to
  -  runscript environment variable `input_dir` is set to `/input/input`
  -  runscript environment variable `output_dir` is set to `/output/output`
  The executed container performs its setup, and when it finishes, sends `"ok"` to `FUM_HOST_IP:FUM_HOST_PORT`
1.  Client requests a new serverless action
2.  FUM server sends a UUID to `FUM_NODE_IP:FUM_NODE_PORT`
3.  Worker node responds with `"ok"`
5.  Worker node performs the work, drawing input from `/input/input` and sending output to `/output/output`
6.  Worker node sends `ok` to `FUM_HOST_IP:FUM_HOST_PORT`
7.  Worker node goes through while and waits for client to request a new serverless action

```
          HOST                          NODE
   launches container -------------------
            |                            |
            |                         (setup)
            |                            |
            |         <------'ok'--------|
            |                            |
            |                            |
      gets request   -------<uuid>------>|
            |         <------'ok'--------|                   
            |                            |
            |                            |
            |                          (run)
            |                            |
            |                            |
            |         <------'ok'--------|
    processes result
```


# fum.py

this is the a python package which provides function `fum_yield()` which must be put inside a
while loop containing the execution code, not including the setup code.

## goodies

`fum.py` instantiates a python object, `Fum` that namespaces some global state for the persistent
fum system.

1.  `Fum.node_port`:  `FUM_NODE_PORT` environment variable
2.  `Fum.node_id`: `FUM_NODE_ID` environment variable
3.  `Fum.node_ip`: `FUM_NODE_IP` environment variable
4.  `Fum.host_port`:  `FUM_HOST_PORT` environment variable
5.  `Fum.host_id`: `FUM_HOST_ID` environment variable
6.  `Fum.current_uuid` : current uuid being worked on
