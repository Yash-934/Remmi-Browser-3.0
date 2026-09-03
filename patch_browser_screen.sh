#!/bin/bash
sed -i -e '/onUrlSubmit = { target ->/,/},/ { /scope.launch(Dispatchers.IO)/,/}/d }' app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt
sed -i -e '/onSearch = { query ->/,/},/ { /scope.launch(Dispatchers.IO)/,/}/d }' app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt
sed -i -e '/onNavigate = { target ->/,/},/ { /scope.launch(Dispatchers.IO)/,/}/d }' app/src/main/java/com/remmi/browser/ui/screens/BrowserScreen.kt
