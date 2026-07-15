# Wraps the stdio-only @xeroapi/xero-mcp-server as a Streamable-HTTP MCP
# endpoint using supergateway. Auth is enforced by the Caddy sidecar
# (docker-compose.yml) — this container itself listens only on the internal
# network.
FROM node:22-slim

# Pin both packages; bump deliberately (the MCP server's tool surface is part
# of your close's audit story).
RUN npm install -g @xeroapi/xero-mcp-server@0.0.16 supergateway@latest

# Xero Custom Connection credentials arrive as env vars at runtime
# (XERO_CLIENT_ID / XERO_CLIENT_SECRET / XERO_SCOPES) — never baked in.

EXPOSE 8000
# Verify flag names against your installed build: npx supergateway --help
CMD ["supergateway", \
     "--stdio", "xero-mcp-server", \
     "--outputTransport", "streamableHttp", \
     "--streamableHttpPath", "/mcp", \
     "--port", "8000"]
