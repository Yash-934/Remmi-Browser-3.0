set -e
export DEBIAN_FRONTEND=noninteractive

# Clean apt lists and install gcc, make, libc6-dev
apt-get update
apt-get install -y gcc g++ make libc6-dev curl

# Install NDK 25.1.8937393
echo "Checking NDK..."
if [ ! -d "$ANDROID_SDK_ROOT/ndk/25.1.8937393" ]; then
    echo "Installing NDK via sdkmanager..."
    yes | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --install "ndk;25.1.8937393"
fi

# Install Rust
echo "Installing Rust..."
if ! command -v rustc >/dev/null 2>&1; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
fi

source "$HOME/.cargo/env"
rustup target add aarch64-linux-android armv7-linux-androideabi x86_64-linux-android

# Check cargo-ndk
if ! command -v cargo-ndk >/dev/null 2>&1; then
    echo "Installing cargo-ndk..."
    cargo install cargo-ndk
fi

echo "=== TOOLCHAIN READY ==="
rustc --version
cargo --version
cargo-ndk --version
