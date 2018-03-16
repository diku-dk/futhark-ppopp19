#!/usr/bin/env python
#
# Reads on stdin JSON as produced by futhark-autotune, and prints on
# stdout it into command-line options that can be passed to
# futhark-bench.

import json
import sys

j = json.load(sys.stdin)
for p in j:
    sys.stdout.write("--pass-option --size=%s=%s " % (p, j[p]))
