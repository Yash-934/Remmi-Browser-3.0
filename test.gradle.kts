plugins {
    id("com.android.application")
}
android {
  testOptions {
    unitTests {
      isIncludeAndroidResources = true
      all {
        it.maxHeapSize = "2g"
      }
    }
  }
}
