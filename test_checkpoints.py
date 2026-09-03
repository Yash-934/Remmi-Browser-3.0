import re

with open("rust/src/lib.rs") as f:
    text = f.read()

cps = re.findall(r'log_checkpoint\([^,]+,\s*"([^"]+)"\)', text)
print("Found checkpoints:", cps)
