#!/bin/sh

set -e

EXP_SUFFIX=`shuf -i0-10000 -n1`
TDIR=/tmp/fumtest
mkdir -p "$TDIR"


echo "testing fallthrough"

python3 test-harness.py 2> /dev/null

echo "testing persistent sends OK"

export FUM_NODE_ID=0
export FUM_NODE_IP=localhost
export FUM_HOST_IP=localhost
export FUM_NODE_PORT=`shuf -i10000-11000 -n1`
export FUM_HOST_PORT=`shuf -i11000-12000 -n1`

ncat -l "$FUM_HOST_PORT" > "$TDIR/ok-result-$EXP_SUFFIX.txt" &

python3 test-harness.py 2> /dev/null &

pid="$!"

sleep  1

pres=`cat $TDIR/ok-result-$EXP_SUFFIX.txt`

[ "$pres" = "ok" ]

#make sure it's still running
ps -p "$pid" > /dev/null

#set up another listener.
ncat -l "$FUM_HOST_PORT" > "$TDIR/ol-result-$EXP_SUFFIX.txt" &

echo "trigger a run"
uuid=`cat /proc/sys/kernel/random/uuid`
echo "$uuid" | ncat localhost "$FUM_NODE_PORT" > "$TDIR/nd-result-$EXP_SUFFIX.txt" 2> /dev/null || true

sleep 1

nres=`cat $TDIR/nd-result-$EXP_SUFFIX.txt`
pres=`cat $TDIR/ol-result-$EXP_SUFFIX.txt`

[ "$nres" = "ok" ]
[ "$pres" = "ok" ]

#make sure it's still running
ps -p "$pid" > /dev/null

#set up another listener.
ncat -l "$FUM_HOST_PORT" > "$TDIR/om-result-$EXP_SUFFIX.txt" &

echo "trigger a run"
uuid=`cat /proc/sys/kernel/random/uuid`
echo "$uuid" | ncat localhost "$FUM_NODE_PORT" > "$TDIR/ne-result-$EXP_SUFFIX.txt" 2> /dev/null || true

sleep 1

nres=`cat $TDIR/ne-result-$EXP_SUFFIX.txt`
pres=`cat $TDIR/om-result-$EXP_SUFFIX.txt`

[ "$nres" = "ok" ]
[ "$pres" = "ok" ]

#make sure it's still running
ps -p "$pid" > /dev/null

echo "tests passed"
