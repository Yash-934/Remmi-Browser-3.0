with open("rust/src/lib.rs", "r") as f:
    text = f.read()

end_idx = text.find("use std::collections::HashSet;")

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
}

"""

text = new_fn + text[end_idx:]
with open("rust/src/lib.rs", "w") as f:
    f.write(text)

print("Applied new_fn successfully!")
