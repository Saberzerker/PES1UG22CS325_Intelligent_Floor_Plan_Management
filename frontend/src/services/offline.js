// IndexedDB + Service Worker
// Offline service worker and IndexedDB management
import { openDB } from 'idb';

const DB_NAME = 'FlooringsDB';
const DB_VERSION = 1;

// Initialize IndexedDB
export const initDB = async () => {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('changes')) {
        db.createObjectStore('changes', { keyPath: 'id', autoIncrement: true });
      }
    },
  });
};

// Store offline changes
export const storeOfflineChange = async (change) => {
  const db = await initDB();
  await db.add('changes', {
    ...change,
    timestamp: new Date(),
    synced: false,
  });
};

// Get all pending changes
export const getPendingChanges = async () => {
  const db = await initDB();
  return await db.getAll('changes');
};

// Mark change as synced
export const markSynced = async (id) => {
  const db = await initDB();
  const change = await db.get('changes', id);
  if (change) {
    change.synced = true;
    await db.put('changes', change);
  }
};

// Clear synced changes
export const clearSyncedChanges = async () => {
  const db = await initDB();
  const changes = await db.getAll('changes');
  for (const change of changes) {
    if (change.synced) {
      await db.delete('changes', change.id);
    }
  }
};

// Sync offline changes
export const syncOfflineChanges = async (api) => {
  const changes = await getPendingChanges();
  if (changes.length === 0) return { synced: [], conflicts: [], failed: [] };

  try {
    const response = await api.post('/api/sync/offline-changes/batch_sync/', {
      changes: changes.map(c => ({
        change_type: c.change_type,
        model_name: c.model_name,
        object_id: c.object_id,
        change_data: c.change_data,
        version_at_change: c.version_at_change,
      }))
    });

    // Mark synced changes
    for (const result of response.data.results.synced) {
      const originalChange = changes.find(c => 
        c.change_type === result.change.change_type &&
        c.model_name === result.change.model_name &&
        c.object_id === result.change.object_id
      );
      if (originalChange) {
        await markSynced(originalChange.id);
      }
    }

    return response.data.results;
  } catch (error) {
    return { synced: [], conflicts: [], failed: changes };
  }
};