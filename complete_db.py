with open('app/src/main/java/com/remmi/browser/storage/RemmiDatabase.kt', 'a') as f:
    f.write('''
@Dao
interface SessionTabDao {
  @Query("DELETE FROM session_tabs WHERE profile = 'GHOST'")
  suspend fun clearPrivateTabs()
  @Query("DELETE FROM session_tabs")
  suspend fun clearAllTabs()
  @Query("SELECT * FROM session_tabs")
  suspend fun getAllTabsList(): List<SessionTabEntity>
}

@Dao
interface ReadingListDao {
  @Query("UPDATE saved_readings SET is_read = :isRead WHERE url = :url")
  suspend fun updateReadStatus(url: String, isRead: Boolean)
  @Query("UPDATE saved_readings SET is_favorite = :isFavorite WHERE url = :url")
  suspend fun toggleFavorite(url: String, isFavorite: Boolean)
  @Query("UPDATE saved_readings SET folder = :folder WHERE url = :url")
  suspend fun updateFolder(url: String, folder: String)
  @Query("DELETE FROM saved_readings WHERE url = :url")
  suspend fun delete(url: String)
  @Query("DELETE FROM saved_readings")
  suspend fun clearAll()
}
''')
