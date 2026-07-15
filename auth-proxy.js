// Bearer-token gate in front of supergateway. Render runs a single process,
// so the Caddy sidecar from docker-compose.yml never runs there — this proxy
// replaces it. Rejects any request whose Authorization header does not match
// MCP_BEARER_TOKEN, then forwards (including SSE streams) to supergateway on
// the internal port.
const http = require("http");

const TOKEN = process.env.MCP_BEARER_TOKEN;
const LISTEN_PORT = process.env.PORT || 8000;   // Render-facing
const UPSTREAM_PORT = 9000;                     // supergateway (internal only)

if (!TOKEN) {
  console.error("FATAL: MCP_BEARER_TOKEN is not set — refusing to start an open proxy.");
  process.exit(1);
}

const server = http.createServer((req, res) => {
  if (req.headers["authorization"] !== `Bearer ${TOKEN}`) {
    res.writeHead(401, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "unauthorized" }));
    return;
  }

  const upstream = http.request(
    { host: "127.0.0.1", port: UPSTREAM_PORT, path: req.url, method: req.method, headers: req.headers },
    (upRes) => {
      res.writeHead(upRes.statusCode, upRes.headers);
      upRes.pipe(res);
    }
  );
  upstream.on("error", (err) => {
    res.writeHead(502, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "upstream unavailable", detail: err.message }));
  });
  req.pipe(upstream);
});

server.listen(LISTEN_PORT, () => {
  console.log(`[auth-proxy] listening on :${LISTEN_PORT}, forwarding to supergateway on :${UPSTREAM_PORT}`);
});
