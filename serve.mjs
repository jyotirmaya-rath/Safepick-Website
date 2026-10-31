// Shows the SafePick website on this computer.
// In this folder run:  node serve.mjs
// It opens the website in your browser. Leave the window open while you look; press Control + C to stop.
// Uses only what comes with Node, so nothing needs installing.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));
const rootPrefix = root.endsWith(sep) ? root : root + sep;
const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.json': 'application/json',
};

async function handle(req, res) {
  let path;
  try {
    path = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch {
    res.writeHead(400).end('Bad request');
    return;
  }
  if (path.endsWith('/')) path += 'index.html';
  const file = normalize(join(root, path));
  if (!file.startsWith(rootPrefix)) {
    res.writeHead(403).end('Not allowed');
    return;
  }
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Not found');
  }
}

// Listen on both 127.0.0.1 and ::1, so "localhost" works whichever one the browser tries first.
function listen(host, port) {
  return new Promise((resolve, reject) => {
    const server = createServer(handle);
    server.once('error', reject);
    server.listen(port, host, () => resolve(server));
  });
}

async function start() {
  const first = Number(process.env.PORT) || 8080;
  for (let port = first; port < first + 20; port++) {
    let v4;
    try {
      v4 = await listen('127.0.0.1', port);
    } catch (err) {
      if (err.code === 'EADDRINUSE') continue;
      throw err;
    }
    try {
      await listen('::1', port);
    } catch (err) {
      if (err.code === 'EADDRINUSE') {
        v4.close();
        continue;
      }
      // no IPv6 on this computer: 127.0.0.1 is enough
    }
    return port;
  }
  throw new Error(`Ports ${first} to ${first + 19} are all in use.`);
}

start()
  .then((port) => {
    const url = `http://localhost:${port}`;
    console.log('');
    console.log(`  SafePick website is running: ${url}`);
    console.log('  Leave this window open while you look. Press Control + C to stop.');
    console.log('');
    if (process.platform === 'darwin' && !process.argv.includes('--no-open')) execFile('open', [url], () => {});
  })
  .catch((err) => {
    console.error(`Could not start the website: ${err.message}`);
    process.exit(1);
  });
