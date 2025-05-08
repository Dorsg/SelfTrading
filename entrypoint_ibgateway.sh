#!/usr/bin/env bash
# entrypoint_ibgateway.sh — start Xvfb then IB‑Gateway

# 1) launch a virtual X server
Xvfb :99 -screen 0 1024x768x16 &

# 2) tell Java to use it
export DISPLAY=:99

# 3) exec the IB‑Gateway java command
exec java \
  -Xmx768m \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:ParallelGCThreads=20 \
  -XX:ConcGCThreads=5 \
  -XX:InitiatingHeapOccupancyPercent=70 \
  -cp "/root/Jts/ibgateway/1026.1h/jars/*:/root/ibc/IBC.jar" \
  ibcalpha.ibc.IbcGateway \
    /root/ibc/config.ini \
    "$TWS_USERID" "$TWS_PASSWORD" paper
