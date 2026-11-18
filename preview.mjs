// Shows the SafePick website on this computer, exactly as it will look at safepick.app.
// Double-click "Preview SafePick website.command", or in this folder run:  node preview.mjs
// Leave the window open while you look; press Control + C to stop. Uses only what comes with Node.
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(fileURLToPath(new URL('.', import.meta.url)), 'site');
const rootPrefix = root.endsWith(sep) ? root : root + sep;
const port = 8080;
const types = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8',
};

async function handle(req, res) {
  let path;
  try {
    path = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch {
    res.writeHead(400).end('Bad request');
    return;
  }
  let file = normalize(join(root, path));
  if (file !== root && !file.startsWith(rootPrefix)) {
    res.writeHead(403).end('Not allowed');
    return;
  }
  try {
    const info = await stat(file);
    if (info.isDirectory()) {
      if (!path.endsWith('/')) {            // /features  ->  /features/
        res.writeHead(301, { Location: path + '/' }).end();
        return;
      }
      file = join(file, 'index.html');
    }
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(body);
  } catch {
    try {
      const body = await readFile(join(root, '404.html'));
      res.writeHead(404, { 'Content-Type': types['.html'] }).end(body);
    } catch {
      res.writeHead(404).end('Not found');
    }
  }
}

createServer(handle).listen(port, '127.0.0.1', () => {
  const url = `http://localhost:${port}`;
  console.log(`SafePick website: ${url}   (Control + C to stop)`);
  execFile('open', [url], () => {});
}).on('error', (err) => {
  console.log(err.code === 'EADDRINUSE' ? `Port ${port} is busy. Close the other preview window and try again.` : String(err));
});
