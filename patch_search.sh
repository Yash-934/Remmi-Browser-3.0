#!/bin/bash
cat app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt | awk '
/onSearch = { query, engine ->/ {
    in_search = 1
}
in_search && /if \(activeTab.profile != PrivacyProfile.GHOST/ {
    skip = 1
}
in_search && skip && /},/ {
    skip = 0
    in_search = 0
    print "            },"
    next
}
skip { next }
/onNavigate = { target ->/ {
    in_nav = 1
}
in_nav && /if \(activeTab.profile != PrivacyProfile.GHOST/ {
    skip_nav = 1
}
in_nav && skip_nav && /},/ {
    skip_nav = 0
    in_nav = 0
    print "            },"
    next
}
skip_nav { next }
{print}
' > app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt.new
mv app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt.new app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt
