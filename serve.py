#!/usr/bin/env python3
"""Serve the NAM blind test app plus a folder of audio files.

usage: python3 serve.py "/path/to/audio folder" [port]
Then open http://localhost:8765 (opens automatically).
"""
import http.server, json, pathlib, re, subprocess, sys, urllib.parse, webbrowser, threading, mimetypes

HERE = pathlib.Path(__file__).resolve().parent
AUDIO = pathlib.Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else HERE
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
EXTS = {'.wav', '.aif', '.aiff', '.flac', '.mp3', '.m4a', '.ogg'}


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, *a):
        pass

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split('?', 1)[0])
        if path in ('/audio', '/audio/'):
            files = sorted(f.name for f in AUDIO.iterdir() if f.is_file() and f.suffix.lower() in EXTS)
            return self._send(200, 'application/json', json.dumps({'dir': str(AUDIO), 'files': files}).encode())
        if path.startswith('/audio/'):
            f = (AUDIO / path[len('/audio/'):]).resolve()
            if not f.is_file() or f.parent != AUDIO:
                return self._send(404, 'text/plain', b'not found')
            ctype = mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(f.stat().st_size))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            with open(f, 'rb') as fh:
                self.copyfile(fh, self.wfile)
            return
        return super().do_GET()

    def do_POST(self):
        path = self.path.split('?', 1)[0]
        try:
            if path == '/api/clips':
                n = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(n) or b'{}')
                clips = [[round(float(s), 3), round(float(l), 3)] for s, l in body.get('clips', []) if float(l) > 0.2]
                trials = max(2, min(60, int(body.get('trials', 16))))
                write_config(clips, trials)
                return self._json(200, {'ok': True, 'clips': len(clips), 'trials': trials})
            if path == '/api/publish':
                return self._json(200, {'ok': True, 'message': publish()})
        except Exception as e:
            return self._json(400, {'error': str(e)})
        return self._json(404, {'error': 'not found'})

    def _json(self, code, obj):
        return self._send(code, 'application/json', json.dumps(obj).encode())


def write_config(clips, trials):
    """Update clips and trials in config.js, leaving everything else as it is."""
    cfg = HERE / 'config.js'
    t = cfg.read_text()
    t = re.sub(r'\n[ \t]*clips:[^\n]*', '', t)
    t = re.sub(r'trials:\s*\d+', f'trials: {trials}', t)
    t = re.sub(r'(clipSeconds:\s*[\d.]+,)', r'\1\n  clips: ' + json.dumps(clips) + ',', t)
    assert 'clips:' in t, 'config.js has no clipSeconds line to anchor clips'
    cfg.write_text(t)


def publish():
    """Commit config.js and push, so GitHub Pages picks up the new clips."""
    def git(*a):
        return subprocess.run(['git', '-C', str(HERE), *a], capture_output=True, text=True)
    if git('diff', '--quiet', '--', 'config.js').returncode == 0:
        return 'No changes since the last publish.'
    r = git('add', 'config.js')
    r = git('-c', 'user.name=Liam Britten', '-c', 'user.email=liambrittenmusic@gmail.com',
            'commit', '-m', 'Update test clips', '--', 'config.js')
    if r.returncode: raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    r = git('push', '-q')
    if r.returncode: raise RuntimeError('committed, but push failed: ' + r.stderr.strip())
    return 'Published. The live test updates in about a minute.'


if __name__ == '__main__':
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H)
    url = f'http://localhost:{PORT}/lab.html'
    print(f'NAM blind test: {url}\naudio folder: {AUDIO}\nCtrl+C to stop')
    if '--no-open' not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
