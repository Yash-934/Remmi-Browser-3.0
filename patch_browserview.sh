#!/bin/bash
cat app/src/main/java/com/remmi/browser/ui/components/BrowserView.kt | awk '
/if \(geckoView.tag != tab.id\)/ {
    print $0
    print "            val oldTabId = geckoView.tag as? String"
    next
}
/scope.launch {/ {
    print $0
    if (in_update) {
        print "              if (oldTabId != null) {"
        print "                geckoEngine.detachView(oldTabId, geckoView)"
        print "              }"
    }
    next
}
/update = { geckoView ->/ {
    in_update = 1
    print $0
    next
}
/onRelease = { geckoView ->/ {
    in_update = 0
    in_release = 1
    print $0
    print "          val currentTag = geckoView.tag as? String ?: tab.id"
    next
}
/geckoEngine.detachView\(tab.id, geckoView\)/ {
    if (in_release) {
        print "            geckoEngine.detachView(currentTag, geckoView)"
        next
    }
}
{print}
' > app/src/main/java/com/remmi/browser/ui/components/BrowserView.kt.new
mv app/src/main/java/com/remmi/browser/ui/components/BrowserView.kt.new app/src/main/java/com/remmi/browser/ui/components/BrowserView.kt
