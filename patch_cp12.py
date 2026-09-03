with open("rust/src/lib.rs", "r") as f:
    content = f.read()

content = content.replace(
    'let out_json = serde_json::to_string(&metrics).unwrap_or_default();',
    'log_checkpoint(&mut env, "CP12_EXIT");\n        let out_json = serde_json::to_string(&metrics).unwrap_or_default();'
)

with open("rust/src/lib.rs", "w") as f:
    f.write(content)
