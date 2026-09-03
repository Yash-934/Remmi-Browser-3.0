package com.remmi.browser.engine

import android.app.Application
import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.remmi.browser.security.ContainerType
import com.remmi.browser.security.PrivacyProfile
import com.remmi.browser.security.SecurityLevel
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mozilla.geckoview.GeckoSession
import org.mozilla.geckoview.GeckoSessionSettings
import org.mozilla.geckoview.GeckoView
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(application = Application::class, sdk = [34])
class ContentProcessRecoveryTests {

  private lateinit var context: Context
  private lateinit var manager: GeckoEngineManager
  private lateinit var tabManager: TabManager

  private val dummyCallbacks = object : GeckoTabCallbacks {
    override fun onUrlChange(url: String) {}
    override fun onTitleChange(title: String) {}
    override fun onProgressChange(progress: Int) {}
    override fun onLoadingChange(isLoading: Boolean) {}
    override fun onSecurityChange(isSecure: Boolean) {}
    override fun onNavStateChange(canGoBack: Boolean, canGoForward: Boolean) {}
    override fun onTrackerBlocked(url: String, type: String) {}
  }

  @Before
  fun setUp() {
    context = ApplicationProvider.getApplicationContext<Application>()
    org.mozilla.gecko.GeckoAppShell.setApplicationContext(context)
    manager = GeckoEngineManager.getInstance(context)
    tabManager = TabManager.getInstance()
    tabManager.closeAllTabs()
    manager.setInitStateForTesting(GeckoEngineManager.GeckoInitState.READY)
  }

  @After
  fun tearDown() = runBlocking {
    manager.uriLoaderForTest = null
    manager.closeAllSessionsSafely()
    tabManager.closeAllTabs()
  }

  /**
   * 1. ContentProcessKillRecoveryTest
   * - Sets up an active tab and GeckoSession.
   * - Triggers onKill on the ContentDelegate.
   * - Asserts that the tab's last known URL is safely reloaded.
   * - Asserts session ownership and view attachment remain intact.
   */
  @Test
  fun testContentProcessKillRecovery_reloadsLastUrlWithoutDuplicatingSession() = runBlocking {
    val tab = tabManager.createTab("about:blank")
    val tabId = tab.id
    val settings = GeckoSessionSettings.Builder().usePrivateMode(true).build()
    val session = GeckoSession(settings)
    manager.setSessionForTesting(tabId, session)

    val loadedUrls = mutableListOf<String>()
    manager.uriLoaderForTest = { _, _, url -> loadedUrls.add(url) }

    val geckoView = GeckoView(context).apply { tag = tabId }
    manager.attachView(
      tabId = tabId,
      geckoView = geckoView,
      profile = PrivacyProfile.SHIELD,
      isDesktopMode = false,
      callbacks = dummyCallbacks,
    )

    val testUrl = "https://example.com/article"
    manager.loadUrl(tabId, testUrl)
    assertEquals(1, loadedUrls.size)
    assertEquals(testUrl, loadedUrls[0])

    // Trigger onKill
    loadedUrls.clear()
    session.contentDelegate?.onKill(session)

    assertEquals("onKill must trigger recovery reload of last URL", 1, loadedUrls.size)
    assertEquals(testUrl, loadedUrls[0])
    assertSame("Session instance must be preserved across kill recovery", session, manager.getSessionForTest(tabId))
    assertTrue("View must remain attached", manager.isViewAttached(tabId))
    assertEquals("Recovered generation must match active generation", manager.getNavGeneration(tabId), manager.getLastRecoveredGeneration(tabId))
  }

  /**
   * 2. ContentProcessCrashRecoveryTest
   * - Sets up an active tab and GeckoSession.
   * - Triggers onCrash on the ContentDelegate.
   * - Asserts that the tab's last known URL is safely reloaded.
   */
  @Test
  fun testContentProcessCrashRecovery_reloadsLastUrl() = runBlocking {
    val tab = tabManager.createTab("about:blank")
    val tabId = tab.id
    val settings = GeckoSessionSettings.Builder().usePrivateMode(true).build()
    val session = GeckoSession(settings)
    manager.setSessionForTesting(tabId, session)

    val loadedUrls = mutableListOf<String>()
    manager.uriLoaderForTest = { _, _, url -> loadedUrls.add(url) }

    val geckoView = GeckoView(context).apply { tag = tabId }
    manager.attachView(
      tabId = tabId,
      geckoView = geckoView,
      profile = PrivacyProfile.SHIELD,
      isDesktopMode = false,
      callbacks = dummyCallbacks,
    )

    val testUrl = "https://example.org/news"
    manager.loadUrl(tabId, testUrl)
    loadedUrls.clear()

    // Trigger onCrash
    session.contentDelegate?.onCrash(session)

    assertEquals("onCrash must trigger recovery reload", 1, loadedUrls.size)
    assertEquals(testUrl, loadedUrls[0])
    assertSame(session, manager.getSessionForTest(tabId))
  }

  /**
   * 3. RecoveryLoopSuppressionTest
   * - Maximum one automatic recovery attempt per navigation generation.
   * - Subsequent onKill / onCrash calls in the same generation must be suppressed.
   * - A new navigation resets suppression for the new generation.
   */
  @Test
  fun testRecoveryLoopSuppression_allowsOnlyOneRecoveryPerGeneration() = runBlocking {
    val tab = tabManager.createTab("about:blank")
    val tabId = tab.id
    val settings = GeckoSessionSettings.Builder().usePrivateMode(true).build()
    val session = GeckoSession(settings)
    manager.setSessionForTesting(tabId, session)

    val loadedUrls = mutableListOf<String>()
    manager.uriLoaderForTest = { _, _, url -> loadedUrls.add(url) }

    val geckoView = GeckoView(context).apply { tag = tabId }
    manager.attachView(
      tabId = tabId,
      geckoView = geckoView,
      profile = PrivacyProfile.SHIELD,
      isDesktopMode = false,
      callbacks = dummyCallbacks,
    )

    val testUrl = "https://example.com/loop-test"
    manager.loadUrl(tabId, testUrl)
    loadedUrls.clear()

    // 1st kill -> should recover
    session.contentDelegate?.onKill(session)
    assertEquals("First kill should trigger recovery", 1, loadedUrls.size)

    // 2nd kill in same generation -> must be suppressed
    loadedUrls.clear()
    session.contentDelegate?.onKill(session)
    assertEquals("Second kill in same generation must be suppressed", 0, loadedUrls.size)

    // 3rd crash in same generation -> must also be suppressed
    session.contentDelegate?.onCrash(session)
    assertEquals("Subsequent crashes in same generation must be suppressed", 0, loadedUrls.size)

    // New navigation increments generation -> resets recovery allowance
    val newUrl = "https://example.com/loop-test-2"
    manager.loadUrl(tabId, newUrl)
    loadedUrls.clear()

    // Kill on new generation -> should recover again
    session.contentDelegate?.onKill(session)
    assertEquals("Kill on new generation should trigger recovery", 1, loadedUrls.size)
    assertEquals(newUrl, loadedUrls[0])
  }

  /**
   * 4. StaleGenerationRecoveryTest
   * - Stale / inactive session receives onKill -> suppressed.
   * - Invalid / blank / about:blank URL -> suppressed.
   */
  @Test
  fun testStaleGenerationRecovery_suppressedForInactiveSessionOrBlankUrl() = runBlocking {
    val tab = tabManager.createTab("about:blank")
    val tabId = tab.id
    val settings = GeckoSessionSettings.Builder().usePrivateMode(true).build()
    val activeSession = GeckoSession(settings)
    manager.setSessionForTesting(tabId, activeSession)

    val loadedUrls = mutableListOf<String>()
    manager.uriLoaderForTest = { _, _, url -> loadedUrls.add(url) }

    val geckoView = GeckoView(context).apply { tag = tabId }
    manager.attachView(
      tabId = tabId,
      geckoView = geckoView,
      profile = PrivacyProfile.SHIELD,
      isDesktopMode = false,
      callbacks = dummyCallbacks,
    )

    // 1. about:blank should NOT trigger recovery reload
    activeSession.contentDelegate?.onKill(activeSession)
    assertTrue("about:blank must not trigger automatic recovery reload", loadedUrls.isEmpty())

    // 2. An inactive/stale session (e.g. previously closed or replaced)
    val staleSession = GeckoSession(settings)
    // Attach dummy delegate mimicking a detached session
    staleSession.contentDelegate = activeSession.contentDelegate

    manager.loadUrl(tabId, "https://example.com/active")
    loadedUrls.clear()

    staleSession.contentDelegate?.onKill(staleSession)
    assertTrue("Stale/inactive session must NOT trigger recovery for active tab", loadedUrls.isEmpty())
  }

  /**
   * 6. GeckoViewTagInvariantTest
   * - Validates checkViewInvariants handles tagged, untagged, and mismatched views safely.
   */
  @Test
  fun testGeckoViewTagInvariant_checksCorrectlyWithoutThrowing() = runBlocking {
    val tab = tabManager.createTab("about:blank")
    val tabId = tab.id
    val settings = GeckoSessionSettings.Builder().usePrivateMode(true).build()
    val session = GeckoSession(settings)
    manager.setSessionForTesting(tabId, session)

    val geckoView = GeckoView(context).apply { tag = tabId }
    manager.attachView(
      tabId = tabId,
      geckoView = geckoView,
      profile = PrivacyProfile.SHIELD,
      isDesktopMode = false,
      callbacks = dummyCallbacks,
    )

    // 1. Tag matches tabId -> invariant ok
    manager.checkViewInvariants(tabId, "TEST_MATCH")

    // 2. Untagged view -> benign initial state
    geckoView.tag = null
    manager.checkViewInvariants(tabId, "TEST_UNTAGGED")

    // 3. Mismatched tag -> logs warning without crashing
    geckoView.tag = "different_tab_id"
    manager.checkViewInvariants(tabId, "TEST_MISMATCH")
  }
}
