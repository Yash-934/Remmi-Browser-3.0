import re

with open("rust/src/lib.rs", "r") as f:
    content = f.read()

# Remove the function log_checkpoint
content = re.sub(r'fn log_checkpoint.*?}\n}\n', '', content, flags=re.DOTALL)
# Remove all log_checkpoint lines
content = re.sub(r'^\s*log_checkpoint\(.*?;\n', '', content, flags=re.MULTILINE)

with open("rust/src/lib.rs", "w") as f:
    f.write(content)
