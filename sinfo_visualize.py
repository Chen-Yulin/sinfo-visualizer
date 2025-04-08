import subprocess
import re
import math
import time
from collections import defaultdict

STATE_CHAR_MAP = {
    'alloc': 'A',
    'mix': 'M',
    'idle': 'I',
    'drain': 'D',
    'drain*': 'D',
    'down': 'X',
    'down*': 'X',
    'resv': 'R',
    'drng': 'D',
    'inval': '!',
    'alloc*': 'A',
}

STATE_COLOR_MAP = {
    'A': '\033[42m',     # green
    'M': '\033[46m',     # cyan
    'D': '\033[43m',     # yellow
    'A': '\033[44m',     # blue
    'X': '\033[41m',     # red
    'R': '\033[45m',     # magenta
    'G': '\033[106m',    # light cyan
    '!': '\033[47;30m',  # white bg, black fg
}
STATE_COLOR_MAP = {
    'I': '\033[42m',     # green
    'M': '\033[46m',     # cyan
    'D': '\033[43m',     # yellow
    'A': '\033[44m',     # blue
    'X': '\033[41m',     # red
    'R': '\033[45m',     # magenta
    'G': '\033[106m',    # light cyan
    '!': '\033[47;30m',  # white bg, black fg
}

def expand_nodelist(nodelist):
    """Expand node[001-003,005] into ['node001', 'node002', 'node003', 'node005']"""
    if '[' not in nodelist:
        return [nodelist]
    match = re.match(r'([a-zA-Z]+)(\[\S+\])', nodelist)
    prefix, body = match.groups()
    result = []
    parts = body.strip('[]').split(',')
    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            for i in range(int(start), int(end)+1):
                result.append(f"{prefix}{i:0{len(start)}d}")
        else:
            result.append(f"{prefix}{part}")
    return result

def parse_sinfo():
    result = subprocess.run(['sinfo', '-h'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')

    partitions = defaultdict(dict)  # partition -> node -> state
    for line in lines:
        parts = line.split()
        if len(parts) < 6:
            continue
        partition, _, _, _, state, nodelist = parts
        nodes = expand_nodelist(nodelist)
        state_char = STATE_CHAR_MAP.get(state, '?')
        for node in nodes:
            if node in partitions[partition]:
                partitions[partition][node] += state_char  # multiple states
            else:
                partitions[partition][node] = state_char
    return partitions

def natural_key(node):
    match = re.match(r"([a-zA-Z]+)(\d+)", node)
    if match:
        prefix, num = match.groups()
        return (prefix, int(num))
    return (node, 0)  # fallback if no match

def render_grid(partition, node_states):
    # ✅ 排序
    nodes = sorted(node_states.items(), key=lambda x: natural_key(x[0]))
    total = len(nodes)
    size = math.ceil(math.sqrt(total))
    print(f"Partition: {partition}")
    print(f"Total nodes: {total}, Grid size: {size}x{size}")
    for i in range(size * size):
        if i < total:
            _, state = nodes[i]
            char = (state[0] if state else '?')
            color = STATE_COLOR_MAP.get(char, '\033[47;30m')  # default: white bg, black ?
            print(f"{color}{char} \033[0m", end='')
        else:
            print(' ', end=' ')
        if (i + 1) % size == 0:
            print()
    print('-' * 40)

def main():
    partitions = parse_sinfo()
    for partition, node_states in partitions.items():
        render_grid(partition, node_states)

if __name__ == "__main__":
    main()

                                                                             111,0-1       Bot
