"""Golden test: sample.tex -> expected.json. Run: python3 tests/test_parser.py"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from parser import parse, ParseError  # noqa: E402


def main():
    with open(os.path.join(HERE, 'sample.tex')) as f:
        got = parse(f.read())
    with open(os.path.join(HERE, 'expected.json')) as f:
        want = json.load(f)
    if got != want:
        print('MISMATCH\n--- got ---')
        print(json.dumps(got, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Structural failures must raise, not return garbage.
    for broken in (r'\name{X}', r'\name{X}\begin{cvsection}{S}\end{cvsection}'):
        try:
            parse(broken)
        except ParseError:
            pass
        else:
            print(f'expected ParseError for: {broken}')
            sys.exit(1)

    print('parser tests OK')


if __name__ == '__main__':
    main()
