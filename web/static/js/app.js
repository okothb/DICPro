// IndexedDB Manager for offline request queueing
class IndexedDBManager {
    constructor(dbName = 'dicpro-offline-queue', storeName = 'requests') {
        this.dbName = dbName;
        this.storeName = storeName;
        this.db = null;
    }

    async openDB() {
        return new Promise((resolve, reject) => {
            if (this.db) {
                return resolve(this.db);
            }
            const request = indexedDB.open(this.dbName, 1);

            request.onerror = (event) => {
                console.error('IndexedDB error:', event.target.error);
                reject('Error opening IndexedDB.');
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id', autoIncrement: true });
                }
            };
        });
    }

    async addRequest(requestData) {
        const db = await this.openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.add(requestData);

            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject('Error adding request to queue: ' + event.target.error);
        });
    }

    async getAllRequests() {
        const db = await this.openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject('Error getting requests from queue: ' + event.target.error);
        });
    }

    async deleteRequest(id) {
        const db = await this.openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete(id);

            request.onsuccess = () => resolve();
            request.onerror = (event) => reject('Error deleting request from queue: ' + event.target.error);
        });
    }
}


// Document Security Suite - Frontend JavaScript (MODERN REDESIGN VERSION)
class DocumentApp {
    constructor() {
        this.currentTab = 'protect';
        this.files = {
            protect: [],
            verify: [],
            extract: [],
            batchProtect: [],
            batchVerify: []
        };
        this.baseURL = this.computeBaseURL();
        this.offlineEnabled = window.__OFFLINE_ENABLED__ || false;
        this.isOnline = navigator.onLine;
        this.hashGenerator = new HashGenerator();

        if (this.offlineEnabled) {
            this.dbManager = new IndexedDBManager();
        }

        this.init();
        this.setupOfflineHandlers();
    }

    computeBaseURL() {
        try {
            if (window.__DOC_API_BASE__) {
                return window.__DOC_API_BASE__;
            }
            // Use relative paths for API calls. This assumes the API is on the same origin.
            return "";
        } catch (e) {
            console.error("Could not determine API base URL:", e);
            return "";
        }
    }

    init() {
        this.setupNavigation(); // UPDATED from setupTabs()
        this.setupFileUploads();
        this.setupButtons();
        this.setupDragAndDrop();
        this.setupEncryptionToggles();
    }

    setupOfflineHandlers() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showAlert('success', '🌐 Back online! Syncing pending operations...', 'protect');
            if (this.offlineEnabled) {
                this.syncPendingOperations();
            }
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showAlert('info', '📱 Working offline. Operations will be queued and synced when connection is restored.', 'protect');
        });
    }

    // NEW function to handle sidebar navigation
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const tabContents = document.querySelectorAll('.tab-content');

        const activateTab = (tabId) => {
            navLinks.forEach(link => {
                if (link.dataset.tab === tabId) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
            tabContents.forEach(content => {
                if (content.id === tabId) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });

            this.currentTab = tabId;
            // Update URL hash without causing page jump
            if (history.pushState) {
                history.pushState(null, null, `#${tabId}`);
            } else {
                window.location.hash = tabId;
            }
        };

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tabId = e.currentTarget.dataset.tab;
                activateTab(tabId);
            });
        });

        const handleHashChange = () => {
            const hash = window.location.hash.substring(1);
            const targetLink = document.querySelector(`.nav-link[data-tab='${hash}']`);
            if (hash && targetLink) {
                activateTab(hash);
            } else {
                activateTab('protect'); // Default tab
            }
        };

        window.addEventListener('hashchange', handleHashChange);
        // Initial load
        handleHashChange();
    }

    setupEncryptionToggles() {
        const encryptPayload = document.getElementById("encryptPayload");
        if (encryptPayload) {
            encryptPayload.addEventListener("change", e => {
                const passwordGroup = document.getElementById("passwordGroup");
                if (passwordGroup) {
                    passwordGroup.style.display = e.target.checked ? "block" : "none";
                }
            });
        }

        const batchEncryptPayload = document.getElementById("batchEncryptPayload");
        if (batchEncryptPayload) {
            batchEncryptPayload.addEventListener("change", e => {
                const batchPasswordGroup = document.getElementById("batchPasswordGroup");
                if (batchPasswordGroup) {
                    batchPasswordGroup.style.display = e.target.checked ? "block" : "none";
                }
            });
        }
    }

    setupFileUploads() {
        const fileInputs = [
            { id: 'protectFileInput', type: 'protect' },
            { id: 'verifyFileInput', type: 'verify' },
            { id: 'extractFileInput', type: 'extract' },
            { id: 'batchProtectFileInput', type: 'batchProtect' },
            { id: 'batchVerifyFileInput', type: 'batchVerify' }
        ];

        fileInputs.forEach(({ id, type }) => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', (e) => this.handleFileSelect(e, type));
            }
        });
    }

    setupButtons() {
        const protectBtn = document.getElementById('protectBtn');
        if (protectBtn) {
            protectBtn.addEventListener('click', () => this.protectDocuments());
        }
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', () => this.verifyDocuments());
        }
        const extractBtn = document.getElementById('extractBtn');
        if (extractBtn) {
            extractBtn.addEventListener('click', () => this.extractData());
        }
        const batchProtectBtn = document.getElementById('batchProtectBtn');
        if (batchProtectBtn) {
            batchProtectBtn.addEventListener('click', () => this.batchProtectDocuments());
        }
        const batchVerifyBtn = document.getElementById('batchVerifyBtn');
        if (batchVerifyBtn) {
            batchVerifyBtn.addEventListener('click', () => this.batchVerifyDocuments());
        }
    }

    setupDragAndDrop() {
        const uploadAreas = [
            { id: 'protectUploadArea', type: 'protect' },
            { id: 'verifyUploadArea', type: 'verify' },
            { id: 'extractUploadArea', type: 'extract' },
            { id: 'batchProtectUploadArea', type: 'batchProtect' },
            { id: 'batchVerifyUploadArea', type: 'batchVerify' }
        ];

        uploadAreas.forEach(({ id, type }) => {
            const area = document.getElementById(id);
            if (area) {
                area.addEventListener('dragover', this.handleDragOver);
                area.addEventListener('dragleave', this.handleDragLeave);
                area.addEventListener('drop', (e) => this.handleDrop(e, type));
            }
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e, type) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        const droppedFiles = Array.from(e.dataTransfer.files);
        const supportedFiles = droppedFiles.filter(file =>
            file.type === 'application/pdf' ||
            file.type.startsWith('image/') ||
            file.type.includes('sheet') ||
            file.type.includes('excel') ||
            file.type === 'text/csv'
        );

        if (supportedFiles.length > 0) {
            this.addFiles(supportedFiles, type);
            if (supportedFiles.length < droppedFiles.length) {
                this.showAlert('warning', 'Some dropped files were not supported and were ignored.', type);
            }
        } else {
            this.showAlert('error', 'Please drop only supported file types (PDF, Images, Excel, CSV).', type);
        }
    }

    handleFileSelect(e, type) {
        const selectedFiles = Array.from(e.target.files);
        if (selectedFiles.length === 0) return;

        const supportedFiles = selectedFiles.filter(file =>
            file.type === 'application/pdf' ||
            file.type.startsWith('image/') ||
            file.type.includes('sheet') ||
            file.type.includes('excel') ||
            file.type === 'text/csv'
        );

        if (supportedFiles.length > 0) {
            this.addFiles(supportedFiles, type);
            if (supportedFiles.length < selectedFiles.length) {
                this.showAlert('warning', 'Some selected files were not supported and were ignored.', type);
            }
        } else {
            this.showAlert('error', 'Please select only supported file types (PDF, Images, Excel, CSV).', type);
        }
        e.target.value = ''; // Reset to allow re-selecting the same file
    }

    addFiles(files, type) {
        if (type === 'protect' || type === 'verify' || type === 'extract') {
            this.files[type] = [files[0]];
        } else {
            this.files[type] = [...this.files[type], ...files];
        }
        this.updateFileList(type);
        this.updateButtonState(type);
    }

    updateFileList(type) {
        const listId = type === 'batchProtect' ? 'batchProtectFileList' :
                      type === 'batchVerify' ? 'batchVerifyFileList' :
                      `${type}FileList`;
        const fileList = document.getElementById(listId);
        if (!fileList) return;
        fileList.innerHTML = '';
        fileList.style.display = this.files[type].length > 0 ? 'block' : 'none';
        this.files[type].forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon"><i class="fas fa-file-${this.getFileIcon(file.type)}"></i></div>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${this.formatFileSize(file.size)}</p>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-secondary btn-sm" onclick="app.removeFile(${index}, '${type}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>`;
            fileList.appendChild(fileItem);
        });
    }

    getFileIcon(mimeType) {
        if (mimeType === 'application/pdf') return 'pdf';
        if (mimeType.startsWith('image/')) return 'image';
        if (mimeType.includes('sheet') || mimeType.includes('excel')) return 'excel';
        if (mimeType === 'text/csv') return 'csv';
        return 'alt';
    }

    removeFile(index, type) {
        this.files[type].splice(index, 1);
        this.updateFileList(type);
        this.updateButtonState(type);
    }

    updateButtonState(type) {
        const buttonIds = {
            protect: 'protectBtn',
            verify: 'verifyBtn',
            extract: 'extractBtn',
            batchProtect: 'batchProtectBtn',
            batchVerify: 'batchVerifyBtn'
        };
        const button = document.getElementById(buttonIds[type]);
        if (button) {
            button.disabled = this.files[type].length === 0;
        }
    }

    validateSecretData(input) {
        if (!input) return { valid: true };
        if (input.length > 10000) {
            return { valid: false, reason: "Secret data too long. Maximum 10,000 characters allowed." };
        }
        const forbiddenPatterns = [
            // Malicious script tags
            /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
            // Event handlers (e.g., onload, onerror)
            /\bon[a-z]+\s*=/gi,
            // Dangerous JavaScript functions and objects
            /\b(eval|exec|document\.cookie|window|location|atob|btoa|setInterval|setTimeout)\b/gi,
            // Shell command execution keywords
            /\b(powershell|cmd|bash|sh|cscript|wsf)\b/gi,
            // Malicious URI schemes
            /(javascript:|vbscript:|data:text\/html|file:)/gi,
            // HTML comments that could hide code
            /<!--/g
        ];
        for (const pattern of forbiddenPatterns) {
            if (pattern.test(input)) {
                return { valid: false, reason: "Secret data contains potentially malicious code or patterns." };
            }
        }
        return { valid: true };
    }

    async apiRequest(endpoint, formData, progressBarId, alertId, resultsId) {
        if (!this.isOnline && this.offlineEnabled) {
            this.showAlert('info', 'You are offline. This operation has been queued.', alertId.replace('Alert', ''));

            const serializableFormData = {};
            for (const [key, value] of formData.entries()) {
                if (value instanceof File) {
                    serializableFormData[key] = {
                        isFile: true,
                        name: value.name,
                        size: value.size,
                        type: value.type,
                        data: await this.fileToByteArray(value)
                    };
                } else {
                    serializableFormData[key] = value;
                }
            }

            await this.dbManager.addRequest({
                endpoint,
                formData: serializableFormData,
                progressBarId,
                alertId,
                resultsId
            });
            return;
        }

        try {
            this.resetAlert(alertId);
            this.updateProgress(progressBarId, 10);
            this.toggleLoading(true);

            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: "POST",
                body: formData
            });

            this.updateProgress(progressBarId, 60);

            const contentType = response.headers.get('content-type');
            if (!response.ok || !contentType || !contentType.includes('application/json')) {
                 const textResponse = await response.text();
                 let errorMessage = `Server error: ${response.status} ${response.statusText}.`;
                 if (textResponse) {
                     errorMessage += ` Details: ${textResponse.substring(0, 100)}...`;
                 }
                 throw new Error(errorMessage);
            }

            const data = await response.json();
            this.updateProgress(progressBarId, 100);

            if (data.success) {
                const successMessage = data.message || "Operation completed successfully.";
                this.showAlert('success', successMessage, alertId.replace('Alert', ''));
                if (resultsId) {
                    this.displayResults(resultsId, data);
                }
            } else {
                const errorMessage = data.detail || data.error || data.message || "An unknown error occurred.";
                this.showAlert('error', errorMessage, alertId.replace('Alert', ''));
            }
        } catch (err) {
            console.error('API request failed:', err);
            const errorMessage = err.message || "Request failed: Check network connection or server status.";
            this.showAlert('error', errorMessage, alertId.replace('Alert', ''));
        } finally {
            this.toggleLoading(false);
            setTimeout(() => this.updateProgress(progressBarId, 0), 1000);
        }
    }

    async fileToByteArray(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                resolve(Array.from(new Uint8Array(event.target.result)));
            };
            reader.onerror = (error) => {
                reject(error);
            };
            reader.readAsArrayBuffer(file);
        });
    }

    escapeHTML(str) {
        if (typeof str !== 'string') return str;
        return str.replace(/[&<>\"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', "'": '&#39;' }[m]));
    }

    displayResults(resultsId, data) {
        const results = document.getElementById(resultsId);
        if (!results) return;
        results.style.display = "block";
        results.innerHTML = "<h3>Results</h3>";
        if (data.results) { // For batch operations
            data.results.forEach(r => {
                const statusClass = r.status === 'success' ? 'status-success' : 'status-error';
                const verificationClass = r.is_verified ? 'status-success' : 'status-warning';
                results.innerHTML += `
                  <div class="result-item">
                    <h4>${r.file || r.file_name}</h4>
                    <p>Status: <span class="status-badge ${statusClass}">${r.status}</span></p>
                    ${r.status === 'success' ? `
                        <p>Verification: <span class="status-badge ${verificationClass}">${r.is_verified ? 'Verified' : 'Tampered/Unknown'}</span></p>
                        <p>Current Hash: ${r.current_hash || 'N/A'}</p>
                        <p>Stored Hash: ${r.stored_hash || 'N/A'}</p>
                        ${r.extracted_data ? `<p>Extracted Data: <textarea readonly class="form-control">${this.escapeHTML(r.extracted_data)}</textarea></p>` : ''}
                        ${r.protected_file_data ? `<a href="data:application/octet-stream;base64,${r.protected_file_data}" class="btn btn-secondary" download="${r.protected_filename}">Download Protected File</a>` : ''}
                    ` : `<p>Error: ${r.error}</p>`}
                  </div>`;
            });
        } else { // For single operations
            const verificationClass = data.is_verified ? 'status-success' : 'status-warning';
            results.innerHTML += `
              <div class="result-item">
                <h4>${data.original_file || data.file_path || 'Document'}</h4>
                ${data.message ? `<p><strong>${data.message}</strong></p>` : ""}
                ${typeof data.is_verified !== "undefined" ? `<p>Status: <span class="status-badge ${verificationClass}">${data.is_verified ? 'VERIFIED' : 'TAMPERED / UNKNOWN'}</span></p>` : ""}
                <p>Original Hash: ${data.original_hash || 'N/A'}</p>
                <p>Protected Hash: ${data.protected_hash || data.current_hash || 'N/A'}</p>
                ${data.protection_date ? `<p>Protection Date: ${new Date(data.protection_date).toLocaleString()}</p>` : ""}
                ${data.extracted_data ? `<p><strong>Extracted Data:</strong><br><textarea class="form-control" readonly>${this.escapeHTML(data.extracted_data)}</textarea></p>` : ''}
                ${data.protected_file_data ? `<a href="data:application/octet-stream;base64,${data.protected_file_data}" class="btn btn-secondary" download="${data.protected_filename}">Download Protected File</a>` : ''}
              </div>`;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showAlert(type, message, context = '') {
        const alertId = context ? `${context}Alert` : `${this.currentTab}Alert`;
        const alert = document.getElementById(alertId);
        if (!alert) return;
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
        alert.style.display = 'flex';
        setTimeout(() => { alert.style.display = 'none'; }, 6000);
    }

    resetAlert(alertId) {
        const el = document.getElementById(alertId);
        if (el) {
            el.style.display = 'none';
            el.innerHTML = '';
        }
    }

    updateProgress(progressBarId, percent) {
        const progressBar = document.getElementById(progressBarId);
        if (progressBar) {
            const parentProgress = progressBar.parentElement;
            if (percent > 0) parentProgress.style.display = 'block';
            progressBar.style.width = `${percent}%`;
            if (percent >= 100 || percent === 0) {
                setTimeout(() => { parentProgress.style.display = 'none'; }, 1000);
            }
        }
    }

    toggleLoading(show) {
        const loading = document.getElementById("loading");
        if (loading) {
            loading.style.display = show ? "block" : "none";
        }
    }

    async protectDocuments() {
        const secretData = document.getElementById("secretData").value;
        const validation = this.validateSecretData(secretData);
        if (!validation.valid) {
            this.showAlert('error', validation.reason, 'protect');
            return;
        }
        if (this.files.protect.length === 0) {
            this.showAlert('error', "Please select a file to protect.", 'protect');
            return;
        }
        const formData = new FormData();
        const file = this.files.protect[0];
        const encrypt = document.getElementById("encryptPayload").checked;
        const password = document.getElementById("encryptionPassword").value;
        const original_hash = await this.hashGenerator.generateFileHash(file);
        formData.append("file", file, file.name);
        formData.append("secret_data", secretData);
        formData.append("encrypt_payload", encrypt);
        formData.append("original_hash", original_hash);
        if (encrypt && password) formData.append("password", password);
        await this.apiRequest("/api/protect", formData, "protectProgressBar", "protectAlert", "protectResults");
    }

    async verifyDocuments() {
        if (this.files.verify.length === 0) {
            this.showAlert('error', "Please select a file to verify.", 'verify');
            return;
        }
        const formData = new FormData();
        const file = this.files.verify[0];
        const current_hash = await this.hashGenerator.generateFileHash(file);
        formData.append("file", file, file.name);
        formData.append("current_hash", current_hash);
        await this.apiRequest("/api/verify", formData, "verifyProgressBar", "verifyAlert", "verifyResults");
    }

    async extractData() {
        if (this.files.extract.length === 0) {
            this.showAlert('error', "Please select a file to extract data from.", 'extract');
            return;
        }
        const formData = new FormData();
        const password = prompt("Enter password if the data is encrypted, otherwise leave blank:");
        const file = this.files.extract[0];
        formData.append("file", file, file.name);
        if (password) {
            formData.append("password", password);
        }
        await this.apiRequest("/api/extract", formData, "extractProgressBar", "extractAlert", "extractResults");
    }

    async batchProtectDocuments() {
        const secretData = document.getElementById("batchSecretData").value;
        const validation = this.validateSecretData(secretData);
        if (!validation.valid) {
            this.showAlert('error', validation.reason, 'batch');
            return;
        }
        if (this.files.batchProtect.length === 0) {
            this.showAlert('error', "Please select files for batch protection", 'batch');
            return;
        }
        const formData = new FormData();
        const files = this.files.batchProtect;
        const encrypt = document.getElementById("batchEncryptPayload").checked;
        const password = document.getElementById("batchEncryptionPassword").value;
        const hashes = await Promise.all(files.map(f => this.hashGenerator.generateFileHash(f)));
        files.forEach(f => formData.append("files", f, f.name));
        hashes.forEach(h => formData.append("original_hashes", h));
        formData.append("secret_data", secretData);
        formData.append('encrypt_payload', encrypt);
        if (encrypt && password) formData.append("password", password);
        await this.apiRequest("/api/batch-protect", formData, "batchProtectProgressBar", "batchAlert", "batchResults");
    }

    async batchVerifyDocuments() {
        if (this.files.batchVerify.length === 0) {
            this.showAlert('error', "Please select files for batch verification", 'batch');
            return;
        }
        const formData = new FormData();
        const files = this.files.batchVerify;
        const hashes = await Promise.all(files.map(f => this.hashGenerator.generateFileHash(f)));
        files.forEach(f => formData.append("files", f, f.name));
        hashes.forEach(h => formData.append("current_hashes", h));
        await this.apiRequest("/api/batch-verify", formData, "batchVerifyProgressBar", "batchAlert", "batchResults");
    }

    async syncPendingOperations() {
        if (!this.offlineEnabled) return;
        const pendingRequests = await this.dbManager.getAllRequests();
        if (pendingRequests.length === 0) return;

        this.showAlert('info', `Syncing ${pendingRequests.length} queued operation(s).`, 'protect');

        for (const req of pendingRequests) {
            try {
                const formData = new FormData();
                for (const key in req.formData) {
                    const value = req.formData[key];
                    if (value.isFile) {
                        const blob = new Blob([new Uint8Array(value.data)], { type: value.type });
                        formData.append(key, blob, value.name);
                    } else {
                        formData.append(key, value);
                    }
                }

                await this.apiRequest(req.endpoint, formData, 'protectProgressBar', 'protectAlert', 'protectResults');
                await this.dbManager.deleteRequest(req.id);
            } catch (error) {
                console.error('Failed to sync operation:', req.id, error);
                this.showAlert('error', `Failed to sync a queued operation. It will be retried later.`, 'protect');
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentApp();

    // Register the service worker
    if ('serviceWorker' in navigator && window.__OFFLINE_ENABLED__) {
        navigator.serviceWorker.register('/sw.js').then(registration => {
            console.log('Service Worker registered with scope:', registration.scope);
        }).catch(error => {
            console.error('Service Worker registration failed:', error);
        });
    }
});
