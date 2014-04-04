ccp - console copy
==================

`ccp` allows you to copy files over interactive sessions with remote UNIX systems. This can be useful when talking to embedded linux systems over serial lines, or when `ssh`/`telnet` is available, but `scp` is not.

Requirements
------------

On the host: `pexpect` python package.

On the target: `base64` and `dd`.

Examples
--------

Transfer a local file to a remote system connected via conserver:

`$ ccp /tmp/data 'console -f ser1':/tmp/data`

Grep in a remote file:

`$ ccp 'screen /dev/ttyS0 115200':/tmp/data - | grep keyword`
