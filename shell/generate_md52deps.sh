#!/usr/bin/env sh
#this script is generate the md5 of rpms in a dir 
#and append them to a file like depends_packages.cfg
#Usage:
#sh generate_md52deps.sh param1 param2
#param1:the dir hold rpms
#param2:the file which you want to append the result to


function append_deps()
{
    if [ -d $1 ];then
        list=`ls $1`
        > $1/append_deps_file
        for i in $list
        do
            if [[ $i =~ ^.*\.rpm$ ]]; then
                echo "[`echo ${i::(-4)}`]" >> $1/append_deps_file
                echo "file = $i" >> $1/append_deps_file
                echo "md5 = `md5sum $1/$i | awk '{print $1}'`" >> $1/append_deps_file
                echo "" >> $1/append_deps_file
            fi
        done
    fi
    if [ -f $2 -a -w $2 ];then
        cat $1/append_deps_file >> $2
    fi
}


append_deps $1 $2
