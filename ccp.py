#!/usr/bin/env python

import argparse
import base64
import re
import sys
import time

import pexpect

class StdioStream(object):
    def pull(self):
        return sys.stdin.read()

    def push(self, data):
        return sys.stdout.write(data)

class LocalStream(object):
    def __init__(self, spec):
        self.spec = spec

    def pull(self):
        return open(self.spec).read()

    def push(self, data):
        open(self.spec, "w").write(data)
    
class ConsoleStream(object):
    PROMPT = re.compile(r"^.*[>#$] $", re.MULTILINE)

    def __init__(self, cmd, spec):
        self.cmd, self.spec = cmd, spec

        self.proc = pexpect.spawn(cmd)
        self.proc.sendline()
        time.sleep(0.5)
        self.proc.expect(ConsoleStream.PROMPT)
        

    def _cmd(self, cmd):
        self.proc.sendline(cmd)
        self.proc.expect(ConsoleStream.PROMPT)
        return self.proc.before[len(cmd):]

    def _stty_raw(self):
        settings  = self._cmd("stty -g").strip()
        self.stty = settings.splitlines()[0].strip()
        self._cmd("stty raw")
        return

    def _stty_restore(self):
        self._cmd("stty " + self.stty)
        return

    def pull(self):
        data = self._cmd("base64 <%s" % self.spec)
        return base64.b64decode(data)

    def push(self, data):
        b64 = base64.b64encode(data)

        self._stty_raw()
        self.proc.sendline("dd bs=1 count=%d | base64 -d >%s" %
                           (len(b64), self.spec))
        self._cmd(b64)
        self._stty_restore()

def stream(spec):
    if spec == "-":
        return StdioStream()
    
    commfile = spec.split(":")

    if   len(commfile) == 1:
        return LocalStream(commfile[0])
    elif len(commfile) == 2:
        return ConsoleStream(commfile[0], commfile[1])

    return None

def get_opts():
    argp = argparse.ArgumentParser(description="""
Console Copy

If COMM is given, it is assumed to be a valid command for interacting
with a remote UNIX like system. If COMM is not given, FILE may be "-";
in which case ccp will use stdio.

Examples:

Transfer a local file to a remote system connected via conserver:
$ ccp /tmp/data 'console -f ser1':/tmp/data

Grep in a remote file:
$ ccp 'screen /dev/ttyS0 115200':/tmp/data - | grep keyword

""", formatter_class=argparse.RawTextHelpFormatter)

    argp.add_argument("src",
                      help="Source to copy from",metavar="[COMM:]FILE")
    argp.add_argument("dst",
                      help="Destination to copy to", metavar="[COMM:]FILE")

    opts = argp.parse_args()
    return opts

def main():
    opts = get_opts()

    data = stream(opts.src).pull()
    stream(opts.dst).push(data)

    sys.exit(0)

if __name__ == '__main__':
    main()
