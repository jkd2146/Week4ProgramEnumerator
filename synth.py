"""Enumerative program synthesizer for the DSL:

    E ::= x | y | 0 | 1 | 2 | + E E | - E E | * E E

Programs are written in Polish (prefix) notation. Input-output examples
are lines of the form "i_1, i_2, o_1". Programs are enumerated in order of
increasing size (number of tokens); the first one consistent with every
example is returned.

Usage: python3 synth.py examples.txt      (or read examples from stdin)
"""
import sys

OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
}


def parse_examples(text):
    examples = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        i1, i2, o1 = (int(p) for p in line.split(","))
        examples.append((i1, i2, o1))
    return examples


def synthesize(examples, max_size=15, prune=True):
    """Return the smallest program (as a string) matching all examples, or None.

    by_size[n] holds every program with exactly n tokens as a pair
    (program string, tuple of its outputs on the examples). Evaluating a
    program is done once, when it is built, from the cached outputs of its
    two subprograms, so nothing is ever re-evaluated from scratch.

    If prune is True, a program whose output vector was already produced by
    an earlier (smaller or equal, earlier-enumerated) program is discarded:
    it can never lead to a solution the earlier one couldn't.
    """
    target = tuple(o for _, _, o in examples)
    seen = set()
    by_size = {}

    def add(size, prog, outs):
        if prune:
            if outs in seen:
                return None
            seen.add(outs)
        by_size[size].append((prog, outs))
        return prog if outs == target else None

    # Size 1: terminals.
    by_size[1] = []
    terminals = [
        ("x", tuple(x for x, _, _ in examples)),
        ("y", tuple(y for _, y, _ in examples)),
        ("0", (0,) * len(examples)),
        ("1", (1,) * len(examples)),
        ("2", (2,) * len(examples)),
    ]
    for prog, outs in terminals:
        if add(1, prog, outs) is not None:
            return prog

    # Size n: an operator token plus subprograms of sizes a and n-1-a.
    for n in range(2, max_size + 1):
        by_size[n] = []
        for op, fn in OPS.items():
            for a in range(1, n - 1):
                b = n - 1 - a
                for lp, lo in by_size[a]:
                    for rp, ro in by_size[b]:
                        outs = tuple(fn(p, q) for p, q in zip(lo, ro))
                        prog = f"{op} {lp} {rp}"
                        if add(n, prog, outs) is not None:
                            return prog
    return None


if __name__ == "__main__":
    text = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    result = synthesize(parse_examples(text))
    print(result if result is not None else "No program found")
