#!/bin/sh

if [ ! -z "${RTSP_URL:-}" ] && [ ! -z "${HOST}" ] && [ ! -z "${TOKEN}" ]; then
  echo "Using RTSP stream from $RTSP_URL"
  exec unifi-cam-proxy --host "$HOST" --model "UVC G4 PTZ" --name "${NAME:-unifi-cam-proxy}" --mac "${MAC:-'AA:BB:CC:00:11:22'}" --cert /client.pem --token "$TOKEN" --ip="192.168.0.222" tapo --username="admin" --password="lcu76dwW6YxMgT" --ffmpeg-args='-c:a copy -c:v copy -bsf:v "h264_metadata=tick_rate=30000/1001"'
fi

exec "$@"
