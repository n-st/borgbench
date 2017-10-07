#!/usr/bin/env python3

import subprocess
import re
from tempfile import TemporaryDirectory
from timeit import default_timer as timer
import sys
import os.path
import errno
import json

def print_header(borg_supports_json=False):
    info_items = []
    info_items += ['Compression setting']
    info_items += ['CHUNK_MIN_EXP']
    info_items += ['CHUNK_MAX_EXP']
    info_items += ['CHUNK_HASH_MASK_BITS']
    if borg_supports_json:
        # JSON format contains raw byte values
        info_items += ['Original size [bytes]']
        info_items += ['Compressed size [bytes]']
        info_items += ['Deduplicated size [bytes]']
    else:
        # Human format contains strings like "123.4 MB"
        info_items += ['Original size']
        info_items += ['Compressed size']
        info_items += ['Deduplicated size']
    info_items += ['Unique chunks']
    info_items += ['Total chunks']
    info_items += ['Duration [seconds]']
    print(';'.join(map(str, info_items)))

def parse_human_output(output_str):
    m = re.match(r'.*This archive: +(\d+\.?\d? .?B) +(\d+\.?\d? .?B) +(\d+\.?\d? .?B).*Chunk index: +(\d+) +(\d+)', output_str, flags=re.DOTALL)
    if m:
        return m.group(1, 2, 3, 4, 5)
    else:
        return None

def parse_json_output(output_str):
    try:
        j = json.loads(output_str)
        return (
                j["archive"]["stats"]["original_size"],
                j["archive"]["stats"]["compressed_size"],
                j["archive"]["stats"]["deduplicated_size"],
                j["cache"]["stats"]["total_unique_chunks"],
                j["cache"]["stats"]["total_chunks"],
            )
    except:
        return None

# single benchmark run
def runConfig(inputdir, compression="none", chunker_params=None, borg_supports_json=False):
    """ If given, chunker_params should be a tuple of (cmin, cmax, cavg). """

    with TemporaryDirectory(prefix='borgbench_') as tempdir:
        returncode = subprocess.call(["borg", "init", "-e", "none", tempdir])
        if returncode != 0:
            sys.stderr.write('`borg init` reported failure\n')
            return

        commandline = ["borg"]
        commandline += ["create", "-v", "-s", "-C", compression]
        if chunker_params:
            commandline += ["--chunker-params=%d,%d,%d,4095" % (chunker_params)]
        if borg_supports_json:
            commandline += ['--json']
        commandline += [tempdir+"::test"]
        commandline += [inputdir]

        env = os.environ.copy()
        env["BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK"] = "yes"

        start = timer()
        proc = subprocess.Popen(commandline, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        output = proc.stdout.read().decode('utf-8')
        errput = proc.stderr.read().decode('utf-8')
        duration = timer() - start

        if borg_supports_json:
            result = parse_json_output(output)
        else:
            result = parse_human_output(errput)

        if result:
            if chunker_params:
                cmin, cmax, cavg = chunker_params
            else:
                cmin, cmax, cavg = 0, 0, 0
            original_size, compressed_size, dedup_size, unique_chunks, total_chunks = result
            info_items = [compression, cmin, cmax, cavg, original_size, compressed_size, dedup_size, unique_chunks, total_chunks, duration]
            print(';'.join(map(str, info_items)))

        else:
            sys.stderr.write('!! Could not parse borg output:\n')
            sys.stderr.write(output)
            sys.stderr.write(errput)

def check_borg_json_support():
    commandline = ["borg"]
    commandline += ['--help']
    proc = subprocess.Popen(commandline, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.stdout.read().decode('utf-8')
    return '--log-json' in output


compression_settings = [
    "none",
    "lz4",
    "zlib,0",
    "zlib,1",
    "zlib,2",
    "zlib,3",
    "zlib,4",
    "zlib,5",
    "zlib,6",
    "zlib,7",
    "zlib,8",
    "zlib,9",
    "lzma,0",
    "lzma,1",
    "lzma,2",
    "lzma,3",
    "lzma,4",
    "lzma,5",
    "lzma,6",
    "lzma,7",
    "lzma,8",
    "lzma,9",
]

chunker_settings = [
    (8, 12, 10),
    (9, 14, 10),
    (8, 13, 11),
    (9, 17, 11),
    (9, 14, 12),
    (10, 17, 12),
    (10, 15, 13),
    (11, 18, 13),
    (11, 16, 14),
    (12, 20, 14),
    (12, 19, 15),
    (13, 20, 16),
    (14, 21, 17),
    (14, 20, 18),
    (15, 21, 19),
    (16, 22, 20),
    (20, 23, 21),
    (18, 18, 18),
]


def print_usage():
    sys.stderr.write(
"""borgbench:
compare speed and efficiency of borgbackup compression and chunker settings

Usage:
    %s <path to testdata>

To produce accurate results for your use case, you need to provide your own
test data.  Create a directory with a collection of files resembling what
you'll be backing up with borg later, then run this script with the test data
directory as an argument.
Ideally, you should store the test data on a tmpfs ("RAM disk") so the results
won't be skewed by your disk speed.
The script will copy your test data to the system's temporary storage, so make
sure there's enough space in there to temporarily store your entire set of test
data.
""" % sys.argv[0])

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(errno.EINVAL)

    testData = sys.argv[1]

    if not os.path.exists(testData):
        sys.stderr.write('The path to your test data (%s) doesn\'t exist.\n')
        print_usage()
        sys.exit(errno.ENOENT)

    borg_supports_json = check_borg_json_support()
    if not borg_supports_json:
        sys.stderr.write("Your version of borg does not yet support the new " +
                "JSON output format (introduced in borg 1.1).\n" +
                "Falling back to parsing human-readable output (which " +
                "doesn't provide byte-accurate values).\n")

    print_header(borg_supports_json=borg_supports_json)

    for params in chunker_settings:
        # Deduplication is done based on the contents of chunks *before* they are
        # compressed, so we don't need to use any compression during the chunker
        # benchmark.
        runConfig(testData, chunker_params=params,
                borg_supports_json=borg_supports_json)

    for comp in compression_settings:
        runConfig(testData, comp, borg_supports_json=borg_supports_json)
