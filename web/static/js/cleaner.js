// This script is designed to unregister all service workers and clear all caches.
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
            registration.unregister();
        }
    });
}

if (window.caches) {
    caches.keys().then(function(names) {
        for (let name of names) {
            caches.delete(name);
        }
    });
}

// Alert the user that the cleanup is complete.
alert("Cleanup script has run. Please wait for the next instruction.");
