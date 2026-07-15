#!/bin/sh
# Runs supergateway on the internal port and the bearer-token proxy on the
# public port. If either process dies, the container exits (Render restarts it).
set -e

supergateway \
  --stdio xero-mcp-server \
  --outputTransport streamableHttp \
  --streamableHttpPath /mcp \
  --port 9000 &

exec node /app/auth-proxy.js
