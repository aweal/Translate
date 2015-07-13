#!/bin/sh

TMP_DIR="/tmp/dbg"


if [[ `mount | grep "$TMP_DIR"` ]]; then
    echo "Mount ready, ready up!"
    exit 0
fi

fn_mount_tfmfs(){
    gksudo "mount -t tmpfs -o size=1m tmpfs $TMP_DIR"
    if [[ $? -eq 0 ]]; then
        echo "Mount ok ;-) ..."
        echo "FULL!"
        cat /dev/urandom > /tmp/dbg/full.log
        if [[ $? -eq 1 ]]; then
            echo "ok ..."
            exit 0

        fi
    else
        echo "Failed moutn tmpfs"
    fi
}


if [ ! -d "$TMP_DIR" ];then
    mkdir "$TMP_DIR"
    if [[ $? -eq 0 ]]; then
        echo "Dir created  ;-) ..."
        fn_mount_tfmfs
    else
        echo "Failed create tmpdir"
    fi
else
    fn_mount_tfmfs
fi



