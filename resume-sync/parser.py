"""mcdowellcv .tex -> resume.json.

Parses the McDowell CV LaTeX structure (\\name/\\address/\\contacts header macros,
cvsection/cvsubsection environments, itemize bullets) into the JSON consumed by the
site's native /resume view. Inline formatting is converted to a whitelisted HTML
subset (<b>, <i>, <a>) — the .tex author is the only input source, but we still only
ever *emit* tags, never pass raw markup through.

Fails loudly (ParseError) on anything structurally unrecognizable so the sync loop
can keep the last good output instead of publishing garbage.
"""

import html
import json
import re


class ParseError(Exception):
    pass


def _strip_comments(tex):
    # % starts a comment unless escaped as \%
    return re.sub(r'(?<!\\)%.*', '', tex)


def _read_group(tex, start):
    """Return (content, index_after_group) for the {...} group starting at tex[start]."""
    if start >= len(tex) or tex[start] != '{':
        raise ParseError(f'expected {{ at offset {start}')
    depth = 0
    for i in range(start, len(tex)):
        c = tex[i]
        if c == '{' and (i == 0 or tex[i - 1] != '\\'):
            depth += 1
        elif c == '}' and tex[i - 1] != '\\':
            depth -= 1
            if depth == 0:
                return tex[start + 1:i], i + 1
    raise ParseError(f'unbalanced braces from offset {start}')


def _macro_args(tex, name, count):
    """Find \\name{a}{b}... and return its args, or None if absent."""
    m = re.search(r'\\' + name + r'\s*(?=\{)', tex)
    if not m:
        return None
    args, pos = [], m.end()
    for _ in range(count):
        while pos < len(tex) and tex[pos] in ' \t\n':
            pos += 1
        arg, pos = _read_group(tex, pos)
        args.append(arg)
    return args


def _inline_to_html(tex):
    """Convert inline LaTeX to plain text with a whitelisted HTML subset."""
    s = tex

    # \href{url}{text} -> <a>
    def href(m):
        url, rest = m.group(1), m.group(2)
        return f'<a href="{html.escape(url, quote=True)}">@@{rest}@@</a>'

    # Iteratively unwrap simple one-arg macros; @@..@@ guards already-built tags.
    for _ in range(10):
        prev = s
        s = re.sub(r'\\href\{([^}]*)\}\{([^{}]*)\}', href, s)
        s = re.sub(r'\\textbf\{([^{}]*)\}', r'<b>\1</b>', s)
        s = re.sub(r'\\textit\{([^{}]*)\}', r'<i>\1</i>', s)
        s = re.sub(r'\\emph\{([^{}]*)\}', r'<i>\1</i>', s)
        s = re.sub(r'\\textsc\{([^{}]*)\}', r'\1', s)
        s = re.sub(r'\\textls(?:\[[^\]]*\])?\{([^{}]*)\}', r'\1', s)
        s = re.sub(r'\\mbox\{([^{}]*)\}', r'\1', s)
        if s == prev:
            break

    s = s.replace(r'\textbar{}', '|').replace(r'\textbar', '|')
    s = s.replace(r'\linebreak', ' ')
    s = s.replace(r'\\', ' ')
    s = s.replace('---', '—').replace('--', '–')
    s = s.replace('~', ' ')
    # unescape LaTeX special chars
    s = re.sub(r'\\([&%$#_{}])', r'\1', s)
    # drop any macro we don't understand, keep flowing text
    s = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?', '', s)
    s = re.sub(r'[{}]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # escape everything, then restore ONLY the tags we generated
    s = html.escape(s, quote=False)
    s = s.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    s = s.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    s = re.sub(r'&lt;a href="([^"]*)"&gt;', r'<a href="\1">', s)
    s = s.replace('&lt;/a&gt;', '</a>')
    s = s.replace('@@', '')
    return s


def _split_lines(group_tex):
    """Split a header group (\\address/\\contacts body) on \\linebreak into html lines."""
    parts = re.split(r'\\linebreak\b', group_tex)
    out = []
    for p in parts:
        h = _inline_to_html(p)
        if h:
            out.append(h)
    return out


def _items(block):
    """Extract \\item bullets from an itemize block."""
    m = re.search(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', block, re.S)
    if not m:
        return []
    bullets = []
    for raw in re.split(r'\\item\b', m.group(1))[1:]:
        h = _inline_to_html(raw)
        if h:
            bullets.append(h)
    return bullets


def parse(tex):
    tex = _strip_comments(tex)

    name_args = _macro_args(tex, 'name', 1)
    if not name_args:
        raise ParseError(r'missing \name{...}')
    name = _inline_to_html(name_args[0])

    contacts = []
    for macro in ('address', 'contacts'):
        args = _macro_args(tex, macro, 1)
        if args:
            contacts.extend(_split_lines(args[0]))

    sections = []
    for sec_m in re.finditer(r'\\begin\{cvsection\}\s*(?=\{)', tex):
        title_raw, pos = _read_group(tex, sec_m.end())
        end_m = re.search(r'\\end\{cvsection\}', tex[pos:])
        if not end_m:
            raise ParseError(f'unclosed cvsection {title_raw!r}')
        body = tex[pos:pos + end_m.start()]

        entries = []
        for sub_m in re.finditer(r'\\begin\{cvsubsection\}\s*(?=\{)', body):
            p = sub_m.end()
            args = []
            for _ in range(3):
                while p < len(body) and body[p] in ' \t\n':
                    p += 1
                a, p = _read_group(body, p)
                args.append(a)
            sub_end = re.search(r'\\end\{cvsubsection\}', body[p:])
            if not sub_end:
                raise ParseError(f'unclosed cvsubsection in section {title_raw!r}')
            sub_body = body[p:p + sub_end.start()]
            entries.append({
                'left': _inline_to_html(args[0]),
                'center': _inline_to_html(args[1]),
                'right': _inline_to_html(args[2]),
                'bullets': _items(sub_body),
            })

        if not entries:
            raise ParseError(f'cvsection {title_raw!r} has no cvsubsections')
        sections.append({'title': _inline_to_html(title_raw), 'entries': entries})

    if not sections:
        raise ParseError('no cvsections found')

    return {'name': name, 'contacts': contacts, 'sections': sections}


if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as f:
        print(json.dumps(parse(f.read()), indent=2, ensure_ascii=False))
