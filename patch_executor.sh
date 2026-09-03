#!/bin/bash
cat app/src/main/java/com/remmi/adblock/BlockExtension.kt | awk '
/networkExecutor.execute {/ {
    print "              try {"
    print $0
    in_exec = 1
    braces = 1
    next
}
in_exec {
    if (/{/ && !/}/) braces++
    if (/}/ && !/{/) braces--
    if (/{/ && /}/) {
        # count { and } individually
        open = gsub(/{/, "{", $0)
        close = gsub(/}/, "}", $0)
        # We cannot easily do this in awk. Let us use a python script or simpler approach.
    }
}
'
