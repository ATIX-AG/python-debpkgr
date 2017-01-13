#!/usr/bin/env python

'''
Python implementation to extract info from .deb

If it fails you get to keep the pieces

pip install python-debian chardet

'''

import os
import sys
import argparse

try:
    from debian import debfile
except Exception:
    print("[ERROR] Failed to import debian\npip install python-debian chardet\n")
    sys.exit()

try:
    # Can't check version so need to support xz
    assert 'xz' in debfile.PART_EXTS
except Exception:
    print("[ERROR] python-debian missing xz support\npip install --upgrade python-debian chardet\n")
    sys.exit()

from debpkg import DebPkg
from aptrepo import create_repo
from aptrepo import index_repo
from aptrepo import parse_repo


def deb_package(args=None):

    __version__ = '0.0.1'
    _usage = ('%(prog)s [options] pkg.deb\n')
    _description = ("Debian Package Infromation Tool\n"
                "Python implementation of dpkg tools\n"
            )
    _prog = "debpkg"

    parser = argparse.ArgumentParser(version="%(prog)s " + __version__,
                                        description=_description,
                                        usage=_usage,
                                        prog=_prog
                                )

    parser.add_argument("-p", "--Package", dest="package", action="store_true",
                    default=False,
                    help="Return apt style Package information")

    parser.add_argument("-n", "--name", dest="name", action="store_true",
                    default=False,
                    help="Return .deb Package Name")

    parser.add_argument("-N", "--nvra", dest="nvra", action="store_true",
                    default=False,
                    help="Return .deb Package nvra")

    parser.add_argument("-f", "--files", dest="files", action="store_true",
                    default=False,
                    help="Return .deb Package File List")

    parser.add_argument("-F", "--file-md5sums", dest="md5sums", action="store_true",
                    default=False,
                    help="Return .deb Package File List with MD5sums")
    
    parser.add_argument("--md5sum", dest="md5sum", action="store_true",
                    default=False,
                    help="Return .deb Package MD5sum")

    parser.add_argument("--sha1", dest="sha1", action="store_true",
                    default=False,
                    help="Return .deb Package sha1")

    parser.add_argument("--sha256", dest="sha256", action="store_true",
                    default=False,
                    help="Return .deb Package sha256")

    parser.add_argument('debpkgs', nargs='?',
                    help="/path/to/pkg.deb pkg.deb... etc")

    args = parser.parse_args()

    steps = {   'md5sum' : args.md5sum,
                'sha1' : args.sha1,
                'sha256' : args.sha256,
                'package' : args.package,
                'name' : args.name,
                'nvra' : args.nvra,
                'files' : args.files,
                'md5sums' : args.md5sums,
        }
                

    if True not in steps.values():
        steps['package'] = True

    if not args.debpkgs:
        pool = 'pool/main'
        if os.path.exists(pool):
            files = [os.path.join(pool, x)
                for x in os.listdir(pool) if x.endswith('.deb')]
        else:
            print("[ERROR] No pool/main directory or *.deb supplied")
            print("%s --help" % _prog)
            sys.exit(1)
    else:
        files = args.debpkgs

    packages = {}

    for fpath in files:
        pkg = DebPkg.from_file(fpath)
        packages.setdefault(pkg.name, pkg)

    for name, pkg in packages.items():
        for step in steps:
            if steps[step]:
                print(getattr(pkg, step))
                  


def apt_indexer(args=None):

    __version__ = '0.0.1'
    _usage = ('%(prog)s [options] /path/*.deb\n')
    _description = ("Apt Repository Creation Tool\n"
                    "Python implementation of apt repo tools\n"
                    )
    _prog = "aptindexer"

    parser = argparse.ArgumentParser(version="%(prog)s " + __version__,
                                     description=_description,
                                     usage=_usage,
                                     prog=_prog
                                     )

    parser.add_argument("-c", "--create", dest="create", action="store_true",
                        default=False,
                        help="Create apt repository metadata")

    parser.add_argument("-i", "--index", dest="index", action="store_true",
                        default=False,
                        help="Index apt repository metadata")

    parser.add_argument("-p", "--parse", dest="parse", action="store_true",
                        default=False,
                        help="Parse apt repository metadata")

    parser.add_argument("-n", "--name", dest="name", action="store",
                        default="stable",
                        help="Specify apt repository name")

    parser.add_argument("-a", "--arches", dest="arches", action="store",
                        default="amd64",
                        help="Specify apt repository architecture")

    parser.add_argument("-D", "--description", dest="desc", action="store",
                        default="Apt Indexer Test Repo",
                        help="Specify apt repository description")


    parser.add_argument('files', nargs='?',
                        help="/path/to/pkg.deb pkg.deb... etc")

    args = parser.parse_args()

    ops = {
        'create': args.create,
        'index': args.index,
        'parse': args.parse,
    }

    name = args.name,
    arches = args.arches,
    description = args.desc

    if True not in ops.values():
        ops['parse'] = True

    files = []

    # if True not in steps.values():
    #    steps['package'] = True

    if ops['create']:    
        if args.files:
            files = args.files
        else:
            pool = 'pool/main'
            files = [os.path.join(pool, x)
                  for x in os.listdir(pool) if x.endswith('.deb')]
        if not len(files):
            print("[ERROR] No pool/main directory or *.deb supplied")
            print("%s --help" % _prog)
            sys.exit(1) 
        create_repo(files, name=name, arches=arches, desc=description)

    if ops['parse']:
        for path in files:
            if os.path.exists(path):
                parse_repo(path)

    if ops['index']:
        for path in files:
            if os.path.exists(path):
                index_repo(path)

if __name__ == "__main__":
    deb_package()
