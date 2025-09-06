// This script is designed to unregister all service workers and clear all caches.
async function cleanupAndRedirect() {
    const statusElement = document.getElementById('statusText');
    
    try {
        if (statusElement) statusElement.textContent = 'Unregistering service workers...';
        
        // Unregister all service workers
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            for (let registration of registrations) {
                await registration.unregister();
            }
        }

        if (statusElement) statusElement.textContent = 'Clearing caches...';
        
        // Clear all caches
        if (window.caches) {
            const cacheNames = await caches.keys();
            for (let name of cacheNames) {
                await caches.delete(name);
            }
        }

        if (statusElement) statusElement.textContent = 'Clearing storage...';
        
        // Clear localStorage and sessionStorage
        localStorage.clear();
        sessionStorage.clear();

        // Clear IndexedDB
        if (window.indexedDB) {
            try {
                const databases = await indexedDB.databases();
                for (const db of databases) {
                    indexedDB.deleteDatabase(db.name);
                }
            } catch (e) {
                console.log('Could not clear IndexedDB:', e);
            }
        }

        if (statusElement) {
            statusElement.textContent = 'Cleanup completed successfully! Redirecting...';
        } else {
            alert("Cache cleanup completed successfully! Redirecting to the main application...");
        }
        
        // Redirect to index.html after a short delay
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);

    } catch (error) {
        console.error('Cleanup error:', error);
        const message = "Cleanup completed with some warnings. Redirecting to the main application...";
        
        if (statusElement) {
            statusElement.textContent = message;
        } else {
            alert(message);
        }
        
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    }
}

// Only run cleanup automatically if we're on the old app.html page or if explicitly called
if (window.location.pathname.includes('app.html') && document.querySelector('h1') && document.querySelector('h1').textContent.includes('Cache Cleanup')) {
    cleanupAndRedirect();
}
