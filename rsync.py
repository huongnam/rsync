#!/usr/bin/env python3
import argparse
import os


def path_dst(dst, basename):
    if os.path.isdir(dst):
        if dst[-1] != '/':
            return dst + '/' + basename
        else:
            return dst + basename
    return dst


def base_name(src):
    if '/' in src:
        return os.path.basename(src)
    return src


def stat(file):
    if not os.path.exists(file):
        return False
    elif os.path.islink(file):
        return os.lstat(file)
    return os.stat(file)


def update_stat(dst, _stat, src):
    if os.path.islink(src):
        os.utime(dst, (_stat.st_atime, _stat.st_mtime), follow_symlinks=False)
    else:
        os.utime(dst, (_stat.st_atime, _stat.st_mtime))
        os.chmod(dst, _stat.st_mode)


def update_content(src, dst):
    f1 = os.open(src, os.O_RDONLY)
    f2 = os.open(dst, os.O_RDWR | os.O_CREAT)
    f1_content = os.read(f1, os.path.getsize(src))
    f2_content = os.read(f2, os.path.getsize(dst))
    length = 0
    while length < os.path.getsize(src):
        os.lseek(f1, length, 0)
        os.lseek(f2, length, 0)
        if length < len(f2_content):
            if f2_content[length] != f1_content[length]:
                os.write(f2, os.read(f1, 1))
        else:
            os.write(f2, os.read(f1, 1))
        length += 1


def copy(src, dst):
    if os.path.islink(src) or os.stat(src).st_nlink > 1:
        if os.path.exists(dst):
            os.unlink(dst)
        if os.path.islink(src):
            _src = os.readlink(src)
            os.symlink(_src, dst)
        elif os.stat(src).st_nlink > 1:
            os.link(src, dst)
    else:
        f1 = os.open(src, os.O_RDONLY)
        if os.path.exists(dst):
            if stat(src).st_size >= stat(dst).st_size:
                update_content(src, dst)
            else:
                os.remove(dst)
                f2 = os.open(dst, os.O_WRONLY | os.O_CREAT)
                os.write(f2, os.read(f1, os.path.getsize(f1)))
        else:
            f2 = os.open(dst, os.O_WRONLY | os.O_CREAT)
            os.write(f2, os.read(f1, os.path.getsize(f1)))


def main():
    parser = argparse.ArgumentParser(prog="rsync", description="namnamnam")
    parser.add_argument("SRC_FILE", type=str)
    parser.add_argument("DESTINATION", type=str)
    parser.add_argument("-c", "--checksum", action='store_true', help='ccc')
    parser.add_argument("-u", "--update", action='store_true', help='uuu')
    args = parser.parse_args()

    src = args.SRC_FILE
    dst = args.DESTINATION
    src_path = os.path.abspath(src)
    dst_path = os.path.abspath(dst)
    if not os.path.exists(src_path):
        print('rsync: link_stat "' +
              src_path + '" failed: No such file or directory (2)')
    elif not os.access(src_path, os.R_OK):
        print('rsync: send_files failed to open "' +
              src_path + '": Permission denied (13)')
    if not os.path.exists(dst) and '/' in dst:
        if dst[-1] == '/':
            os.mkdir(dst)
        else:
            if not os.path.exists(os.path.dirname(dst)):
                os.mkdir(os.path.dirname(dst))
    dst = path_dst(dst, base_name(src))
    if not os.path.exists(dst):
        os.open(dst, os.O_CREAT)
    if args.update:
        if stat(src).st_mtime > stat(dst).st_mtime:
            copy(src, dst)
    elif args.checksum:
        copy(src, dst)
    else:
        if (stat(src).st_mtime != stat(dst).st_mtime) or (
           stat(src).st_size != stat(dst).st_size):
            copy(src, dst)
    update_stat(dst, stat(src), src)


main()
