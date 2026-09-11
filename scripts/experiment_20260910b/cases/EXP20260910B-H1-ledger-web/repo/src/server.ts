import { readFileSync } from "node:fs";
import { createServer } from "node:http";

// Settings come exclusively from deploy/config.<NODE_ENV>.json.
// No defaults: a value not present in the file is a fatal startup error.
interface ServerConfig {
  host: string;
  port: number;
  tls: boolean;
}

export function loadConfig(env: string): ServerConfig {
  const raw = JSON.parse(
    readFileSync(`deploy/config.${env}.json`, "utf8"),
  ) as Partial<ServerConfig>;

  const problems: string[] = [];
  if (typeof raw.host !== "string" || raw.host.length === 0)
    problems.push("host: required");
  if (typeof raw.port !== "number" || !Number.isInteger(raw.port))
    problems.push("port: required integer");
  if (typeof raw.tls !== "boolean") problems.push("tls: required boolean");
  if (problems.length > 0)
    throw new Error(`invalid config.${env}.json -> ${problems.join("; ")}`);

  return raw as ServerConfig;
}

export function start(cfg: ServerConfig): void {
  createServer((_req, res) => {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: true }));
  }).listen(cfg.port, cfg.host, () => {
    console.log(`ledger-web listening on ${cfg.host}:${cfg.port} tls=${cfg.tls}`);
  });
}
