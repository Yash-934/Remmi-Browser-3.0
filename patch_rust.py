import re

with open("rust/src/lib.rs", "r") as f:
    text = f.read()

# Replace log_checkpoint definition
old_fn_regex = r'fn log_checkpoint\(env: &mut jni::JNIEnv, name: &str\) \{[\s\S]*?\}\}'

new_fn = """extern "C" {
    fn __android_log_print(prio: std::os::raw::c_int, tag: *const std::os::raw::c_char, fmt: *const std::os::raw::c_char, ...) -> std::os::raw::c_int;
}

fn log_checkpoint(name: &str) {
    let pid = std::process::id();
    let tid = unsafe { libc::gettid() };
    let time_ms = match std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH) {
        Ok(d) => d.as_millis() as u64,
        Err(_) => 0,
    };
    let mut rss_pages: usize = 0;
    if let Ok(contents) = std::fs::read_to_string("/proc/self/statm") {
        if let Some(rss_str) = contents.split_whitespace().nth(1) {
            if let Ok(p) = rss_str.parse::<usize>() {
                rss_pages = p;
            }
        }
    }
    let rss_mb = (rss_pages * 4096) / (1024 * 1024);

    let mut pss_kb: u64 = 0;
    if let Ok(smaps) = std::fs::read_to_string("/proc/self/smaps_rollup") {
        for line in smaps.lines() {
            if line.starts_with("Pss:") {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 2 {
                    if let Ok(k) = parts[1].parse::<u64>() {
                        pss_kb = k;
                        break;
                    }
                }
            }
        }
    }
    let pss_mb = pss_kb / 1024;

    let tag = b"AdblockNative\\0";
    let fmt = b"[NATIVE_CHECKPOINT] %s | timestamp=%llu | pid=%u | tid=%d | rss=%zuMB | pss=%lluMB\\n\\0";
    let mut name_buf = [0u8; 64];
    let name_bytes = name.as_bytes();
    let copy_len = std::cmp::min(name_bytes.len(), 63);
    name_buf[..copy_len].copy_from_slice(&name_bytes[..copy_len]);

    unsafe {
        __android_log_print(
            4, // ANDROID_LOG_INFO
            tag.as_ptr() as *const std::os::raw::c_char,
            fmt.as_ptr() as *const std::os::raw::c_char,
            name_buf.as_ptr() as *const std::os::raw::c_char,
            time_ms,
            pid,
            tid,
            rss_mb,
            pss_mb,
        );
    }
}"""

match = re.search(old_fn_regex, text)
if match:
    text = text[:match.start()] + new_fn + text[match.end():]
    print("Replaced log_checkpoint definition!")
else:
    print("Could not match old_fn_regex!")

# Replace calls: log_checkpoint(&mut env, "CP...") -> log_checkpoint("CP...")
text = re.sub(r'log_checkpoint\(&mut env,\s*("CP\d+_[A-Z_]+")\)', r'log_checkpoint(\1)', text)

with open("rust/src/lib.rs", "w") as f:
    f.write(text)

print("Updated calls successfully!")
