while ps aux | grep -E "cargo|rustc" | grep -v grep >/dev/null; do
    sleep 3
done
echo "Cargo finished!"
