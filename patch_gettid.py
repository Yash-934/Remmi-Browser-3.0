with open("rust/src/lib.rs", "r") as f:
    text = f.read()

old_code = """extern "C" {
    fn __android_log_print(prio: std::os::raw::c_int, tag: *const std::os::raw::c_char, fmt: *const std::os::raw::c_char, ...) -> std::os::raw::c_int;
}

fn log_checkpoint(name: &str) {
    let pid = std::process::id();
    let tid = unsafe { libc::gettid() };"""

new_code = """extern "C" {
    fn __android_log_print(prio: std::os::raw::c_int, tag: *const std::os::raw::c_char, fmt: *const std::os::raw::c_char, ...) -> std::os::raw::c_int;
    fn gettid() -> i32;
}

fn log_checkpoint(name: &str) {
    let pid = std::process::id();
    let tid = unsafe { gettid() };"""

if old_code in text:
    text = text.replace(old_code, new_code)
    with open("rust/src/lib.rs", "w") as f:
        f.write(text)
    print("Replaced gettid successfully!")
else:
    print("Could not find old_code!")
