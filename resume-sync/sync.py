"""Poll the resume repo; on a new commit compile + parse + publish.

Cycle: fetch → if remote SHA differs from last published → copy worktree to a build
dir, make the .cls XeTeX-safe (tectonic can't do microtype letterspacing), compile
with tectonic, parse to resume.json, then atomically publish resume.pdf +
resume.json into OUT_DIR (the site's content volume). Any failure keeps the last
good outputs in place — the live site never sees a broken state.

Env: REPO_URL (ssh), OUT_DIR=/out, STATE_DIR=/state, POLL_SECONDS=60, RUN_ONCE=0
SSH key + known_hosts are expected under STATE_DIR/ssh (mounted, provisioned once).
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

from parser import parse

REPO_URL = os.environ['REPO_URL']
OUT_DIR = os.environ.get('OUT_DIR', '/out')
STATE_DIR = os.environ.get('STATE_DIR', '/state')
POLL_SECONDS = int(os.environ.get('POLL_SECONDS', '60'))
RUN_ONCE = os.environ.get('RUN_ONCE', '0') == '1'

REPO_DIR = os.path.join(STATE_DIR, 'repo')
SHA_FILE = os.path.join(STATE_DIR, 'published-sha')
GIT_ENV = {
    **os.environ,
    'GIT_SSH_COMMAND': (
        f'ssh -i {STATE_DIR}/ssh/id_ed25519 '
        f'-o UserKnownHostsFile={STATE_DIR}/ssh/known_hosts -o IdentitiesOnly=yes'
    ),
}


def log(msg):
    print(f'[{datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}] {msg}', flush=True)


def git(*args, cwd=REPO_DIR):
    return subprocess.run(['git', *args], cwd=cwd, env=GIT_ENV, check=True,
                          capture_output=True, text=True).stdout.strip()


def ensure_repo():
    if not os.path.isdir(os.path.join(REPO_DIR, '.git')):
        log(f'cloning {REPO_URL}')
        subprocess.run(['git', 'clone', '--depth', '1', REPO_URL, REPO_DIR],
                       env=GIT_ENV, check=True, capture_output=True, text=True)


def published_sha():
    try:
        with open(SHA_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def xetex_safe_cls(build_dir):
    """microtype letterspacing (\\textls) is unsupported on XeTeX/tectonic."""
    cls = os.path.join(build_dir, 'mcdowellcv.cls')
    with open(cls) as f:
        content = f.read()
    content = re.sub(r'\\textls(?:\[[^\]]*\])?\{(\\textsc\{\\@name\})\}', r'\1', content)
    with open(cls, 'w') as f:
        f.write(content)


def build_and_publish(sha):
    with tempfile.TemporaryDirectory() as build_dir:
        for name in os.listdir(REPO_DIR):
            if name != '.git':
                src = os.path.join(REPO_DIR, name)
                dst = os.path.join(build_dir, name)
                shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)

        xetex_safe_cls(build_dir)

        subprocess.run(['tectonic', 'resume.tex'], cwd=build_dir, check=True,
                       capture_output=True, text=True)
        pdf = os.path.join(build_dir, 'resume.pdf')

        with open(os.path.join(build_dir, 'resume.tex')) as f:
            data = parse(f.read())
        data['sourceCommit'] = sha
        data['generatedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')

        # Atomic publish: write into OUT_DIR then rename (same filesystem).
        os.makedirs(OUT_DIR, exist_ok=True)
        tmp_json = os.path.join(OUT_DIR, '.resume.json.tmp')
        with open(tmp_json, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        tmp_pdf = os.path.join(OUT_DIR, '.resume.pdf.tmp')
        shutil.copy2(pdf, tmp_pdf)
        os.replace(tmp_pdf, os.path.join(OUT_DIR, 'resume.pdf'))
        os.replace(tmp_json, os.path.join(OUT_DIR, 'resume.json'))

    with open(SHA_FILE, 'w') as f:
        f.write(sha)
    log(f'published {sha[:10]}')


def cycle():
    ensure_repo()
    git('fetch', '--depth', '1', 'origin')
    git('reset', '--hard', 'origin/HEAD')
    sha = git('rev-parse', 'HEAD')
    if sha == published_sha():
        return False
    log(f'new commit {sha[:10]} (was {(published_sha() or "none")[:10]})')
    build_and_publish(sha)
    return True


def main():
    log(f'resume-sync starting; repo={REPO_URL} poll={POLL_SECONDS}s once={RUN_ONCE}')
    while True:
        try:
            cycle()
        except subprocess.CalledProcessError as e:
            log(f'ERROR (kept last good output): {e}\n{(e.stderr or "")[-800:]}')
            if RUN_ONCE:
                sys.exit(1)
        except Exception as e:
            log(f'ERROR (kept last good output): {type(e).__name__}: {e}')
            if RUN_ONCE:
                sys.exit(1)
        if RUN_ONCE:
            return
        time.sleep(POLL_SECONDS)


if __name__ == '__main__':
    main()
