import os, subprocess

print("Checking toolchains...")
for cmd in ["cargo", "rustc", "cargo-ndk", "ndk-build", "clang"]:
    res = subprocess.run(["which", cmd], capture_output=True, text=True)
    print(f"which {cmd}: {res.returncode} -> {res.stdout.strip()}")

print("\nChecking /opt and /usr for ndk or rust:")
for root_dir in ["/opt", "/usr/local"]:
    if os.path.exists(root_dir):
        for item in os.listdir(root_dir):
            print(f"  {root_dir}/{item}")

