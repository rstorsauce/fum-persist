# fum-persist
persistence tools for fum

persistence protocol:
--------------------

0.  Setup of the serverless function:  Executed with the following environment variables set:
  -  `FUM_NODE`: node number (usually 0..7)
  -  `FUM_NODE_IP`: IP address of this node
  -  `FUM_PORT_NODE`: IP port that the serverless function will listen on.
  -  `FUM_HOST`: IP address of the FUM server
  -  `FUM_PORT`: IP port that the FUM server will listen to
  -  runscript environment variable `input_dir` is set to `/input/input`
  -  runscript environment variable `output_dir` is set to `/output/output` 
  The executed container performs its setup, and when finishes, sends `FUM_NODE` to `FUM_HOST:FUM_PORT`
1.  Client requests a new serverless action
2.  FUM server sends a UUID to `FUM_NODE_IP:FUM_PORT_NODE`
3.  Worker node refreshes the network filesystem cache and responds with 'ok'
4.  Worker node checks to make sure `/input/input` and `/output/output` are symlink-mapped to `/input/<uuid>` and `/output/<uuid>`
5.  Worker node performs the work, drawing input from `/input/input` and sending output to `/output/output`
6.  Worker node sends `FUM_NODE` to `FUM_HOST:FUM_PORT`
7.  Worker node goes through while and waits for client to request a new serverless action

# fum.py

provides function `fum_yield()` which must be put inside a while loop containing the execution code, not including the setup code.
