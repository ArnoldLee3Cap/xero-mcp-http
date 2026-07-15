# Wraps the stdio-only @xeroapi/xero-mcp-server as a Streamable-HTTP MCP
# endpoint using supergateway, with a bearer-token auth proxy in front
# (auth-proxy.js — single-process platforms like Render never run the Caddy
# sidecar from docker-compose.yml, so auth must live inside this container).
FROM node:22-slim

# Pin both packages; bump deliberately (the MCP server's tool surface is part
# of your close's audit story).
RUN npm install -g @xeroapi/xero-mcp-server@0.0.16 supergateway@latest

# Xero Custom Connection credentials arrive as env vars at runtime
# (XERO_CLIENT_ID / XERO_CLIENT_SECRET / XERO_SCOPES / MCP_BEARER_TOKEN)
# — never baked in.

WORKDIR /app
COPY auth-proxy.js start.sh ./
RUN chmod +x start.sh

EXPOSE 8000
CMD ["/app/start.sh"]
