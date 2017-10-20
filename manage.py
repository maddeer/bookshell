#!/usr/bin/env python3 

from migrate.versioning.shell import main

main(url='sqlite:///model/bookshell.db', repository='./migrations/')
