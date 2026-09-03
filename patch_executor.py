import re

with open('app/src/main/java/com/remmi/adblock/BlockExtension.kt', 'r') as f:
    content = f.read()

target = """              inflightDecisionCount.incrementAndGet()
              networkExecutor.execute {"""

replacement = """              try {
                networkExecutor.execute {
                  inflightDecisionCount.incrementAndGet()
                  try {"""

content = content.replace(target, replacement)

# We also need to fix the closing brace.
# The original block ends with:
#                 } finally {
#                   inflightDecisionCount.decrementAndGet()
#                 }
#               }
#             }
#             "GET_COSMETIC_RESOURCES" -> {

target_end = """                } finally {
                  inflightDecisionCount.decrementAndGet()
                }
              }
            }
            "GET_COSMETIC_RESOURCES" -> {"""

replacement_end = """                } finally {
                  inflightDecisionCount.decrementAndGet()
                }
              }
              } catch (e: java.util.concurrent.RejectedExecutionException) {
                Log.w(TAG, "[NETWORK_QUEUE_SATURATED] Rejecting SHOULD_BLOCK for $url. aggressive=$aggressive")
                val cancelRequest = aggressive // fail-closed if aggressive (GHOST/TOR), else fail-open
                val resp = JSONObject().apply {
                  put("type", "SHOULD_BLOCK_RESULT")
                  put("ok", true)
                  put("cancel", cancelRequest)
                  put("ruleId", if (cancelRequest) "queue_saturated_fail_closed" else "queue_saturated_fail_open")
                  put("ruleSource", "AdblockQueue")
                  put("generation", reqPortGen)
                  put("requestId", requestId)
                  put("portGeneration", reqPortGen)
                  put("jsInstanceId", jsInstanceId)
                  put("instanceId", instId)
                  put("nativeStartTimestamp", startTs)
                  put("nativeEndTimestamp", System.currentTimeMillis())
                  put("responseDeliveryTimestamp", System.currentTimeMillis())
                }
                mainHandler.post {
                  synchronized(portLock) {
                    if (activePort == p) {
                      try { p.postMessage(resp) } catch (ex: Exception) {}
                    }
                  }
                }
              }
            }
            "GET_COSMETIC_RESOURCES" -> {"""

content = content.replace(target_end, replacement_end)

with open('app/src/main/java/com/remmi/adblock/BlockExtension.kt', 'w') as f:
    f.write(content)
