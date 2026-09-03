with open("rust/src/lib.rs", "r") as f:
    code = f.read()

# Replace log_checkpoint implementation
old_fn = """fn log_checkpoint(env: &mut jni::JNIEnv, name: &str) {
    let pid = std::process::id();
    let tid = unsafe { libc::gettid() };
    let time_ms = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis();
    let mut rss_mb = 0;
    if let Ok(contents) = std::fs::read_to_string("/proc/self/statm") {
        if let Some(rss_pages_str) = contents.split_whitespace().nth(1) {
            if let Ok(rss_pages) = rss_pages_str.parse::<usize>() {
                rss_mb = (rss_pages * 4096) / (1024 * 1024);
            }
        }
    }
    
    let msg = format!("[NATIVE_CHECKPOINT] {} | time={} | pid={} | tid={} | rss={}MB", name, time_ms, pid, tid, rss_mb);
    if let Ok(j_tag) = env.new_string("AdblockNative") {
        if let Ok(j_msg) = env.new_string(msg) {
            let _ = env.call_static_method(
                "android/util/Log",
                "i",
                "(Ljava/lang/String;Ljava/lang/String;)I",
                &[jni::objects::JValue::from(&j_tag), jni::objects::JValue::from(&j_msg)]
            );
        }
    }
}"""

new_fn = """fn log_checkpoint(name: &str) {
    let pid = std::process::id();
    let tid = unsafe { libc::gettid() };
    let time_ms = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis();
    let mut rss_pages: usize = 0;
    if let Ok(contents) = std::fs::read_to_string("/proc/self/statm") {
        if let Some(rss_str) = contents.split_whitespace().nth(1) {
            if let Ok(p) = rss_str.parse::<usize>() {
                rss_pages = p;
            }
        }
    }
    let rss_mb = (rss_pages * 4096) / (1024 * 1024);
    
    // Read PSS from /proc/self/smaps_rollup if available
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

    // Use raw Android __android_log_print to avoid allocating JString or calling JNI
    use std::ffi::CString;
    let tag = CString::new("AdblockNative").unwrap();
    let fmt = CString::new("[NATIVE_CHECKPOINT] %s | timestamp=%llu | pid=%u | tid=%d | rss=%zuMB | pss=%lluMB").unwrap();
    let name_c = CString::new(name).unwrap();
    unsafe {
        libc::__android_log_print(
            4, // ANDROID_LOG_INFO
            tag.as_ptr(),
            fmt.as_ptr(),
            name_c.as_ptr(),
            time_ms as u64,
            pid,
            tid,
            rss_mb,
            pss_mb,
        );
    }
}"""

if old_fn in code:
    code = code.replace(old_fn, new_fn)
    code = code.replace('log_checkpoint(&mut env, ', 'log_checkpoint(')
    with open("rust/src/lib.rs", "w") as f:
        f.write(code)
    print("Replaced successfully!")
else:
    print("Old fn not matched exactly, checking diff...")
