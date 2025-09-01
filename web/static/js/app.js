// Document Security Suite - Frontend JavaScript (FIXED VERSION)
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
        // Determine API base URL depending on environment
        this.baseURL = this.computeBaseURL();
        this.offlineEnabled = window.__OFFLINE_ENABLED__ || false;
        this.isOnline = navigator.onLine;
        this.pendingOperations = [];
        
        this.init();
        this.setupOfflineHandlers();
    }

    computeBaseURL() {
        try {
            // Allow manual override via a global if provided in HTML
            if (window.__DOC_API_BASE__) {
                return window.__DOC_API_BASE__;
            }

            const { protocol, hostname, port } = window.location;

            // Local development: static site on 8080, API on 8000
            const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
            if (isLocalhost) {
                // If we're not already on the API port, point to FastAPI
                if (port && port !== '8000') {
                    return `${protocol}//${hostname}:8000`;
                }
                return `${protocol}//${hostname}:${port || '8000'}`;
            }

            // Production or any non-local host: default to Netlify Functions path
            return '/.netlify/functions/api';
        } catch (e) {
            // Safe fallback in case window is unavailable
            return '/.netlify/functions/api';
        }
    }

    init() {
        this.setupTabs();
        this.setupFileUploads();
        this.setupButtons();
        this.setupDragAndDrop();
        this.setupEncryptionToggles();
        this.setupHashManagement();
    }   
 setupOfflineHandlers() {
        // Monitor online/offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showAlert('success', '🌐 Back online! Syncing pending operations...', 'protect');
            this.syncPendingOperations();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showAlert('info', '📱 Working offline. Operations will sync when connection is restored.', 'protect');
        });

        // Initial online status check
        this.updateOnlineStatus();
    }

    updateOnlineStatus() {
        const statusIndicator = document.getElementById('onlineStatus');
        if (statusIndicator) {
            statusIndicator.textContent = this.isOnline ? '🌐 Online' : '📱 Offline';
            statusIndicator.className = this.isOnline ? 'status-online' : 'status-offline';
        }
    }

    setupHashManagement() {
        // Hash management buttons
        const refreshStatsBtn = document.getElementById('refreshStatsBtn');
        if (refreshStatsBtn) {
            refreshStatsBtn.addEventListener('click', () => this.loadHashStats());
        }

        const syncAllBtn = document.getElementById('syncAllBtn');
        if (syncAllBtn) {
            syncAllBtn.addEventListener('click', () => this.syncAllHashes());
        }

        const refreshSyncBtn = document.getElementById('refreshSyncBtn');
        if (refreshSyncBtn) {
            refreshSyncBtn.addEventListener('click', () => this.loadSyncStatus());
        }

        const viewAllHashesBtn = document.getElementById('viewAllHashesBtn');
        if (viewAllHashesBtn) {
            viewAllHashesBtn.addEventListener('click', () => this.viewAllHashes());
        }

        const exportHashesBtn = document.getElementById('exportHashesBtn');
        if (exportHashesBtn) {
            exportHashesBtn.addEventListener('click', () => this.exportHashes());
        }

        const cleanupBtn = document.getElementById('cleanupBtn');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => this.cleanupOldHashes());
        }

        const closeHashListBtn = document.getElementById('closeHashListBtn');
        if (closeHashListBtn) {
            closeHashListBtn.addEventListener('click', () => {
                document.getElementById('hashListModal').style.display = 'none';
            });
        }

        // Load initial data when hash tab is opened
        this.loadHashManagementData();
    }    se
tupTabs() {
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.dataset.tab;

                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                const targetContent = document.getElementById(tabId);
                if (targetContent) {
                    targetContent.classList.add('active');
                }

                this.currentTab = tabId;

                // Load hash management data when switching to hashes tab
                if (tabId === 'hashes') {
                    this.loadHashManagementData();
                }
            });
        });
    }

    setupEncryptionToggles() {
        // Setup encryption toggles for password groups
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
    }    setup
FileUploads() {
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
        // Protect button
        const protectBtn = document.getElementById('protectBtn');
        if (protectBtn) {
            protectBtn.addEventListener('click', () => this.protectDocuments());
        }

        // Verify button
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', () => this.verifyDocuments());
        }

        // Extract button
        const extractBtn = document.getElementById('extractBtn');
        if (extractBtn) {
            extractBtn.addEventListener('click', () => this.extractData());
        }

        // Batch protect button
        const batchProtectBtn = document.getElementById('batchProtectBtn');
        if (batchProtectBtn) {
            batchProtectBtn.addEventListener('click', () => this.batchProtectDocuments());
        }

        // Batch verify button
        const batchVerifyBtn = document.getElementById('batchVerifyBtn');
        if (batchVerifyBtn) {
            batchVerifyBtn.addEventListener('click', () => this.batchVerifyDocuments());
        }

        // Note: Test API button removed as requested
    }    s
etupDragAndDrop() {
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

        const files = Array.from(e.dataTransfer.files).filter(file =>
            file.type === 'application/pdf' ||
            file.type.startsWith('image/') ||
            file.type.includes('sheet') ||
            file.type.includes('excel') ||
            file.type === 'text/csv'
        );

        if (files.length > 0) {
            this.addFiles(files, type);
        } else {
            this.showAlert('error', 'Please drop only supported file types (PDF, Images, Excel, CSV).', type);
        }
    }

    handleFileSelect(e, type) {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            this.addFiles(files, type);
        }
    }    
addFiles(files, type) {
        if (type === 'protect' || type === 'verify' || type === 'extract') {
            this.files[type] = [files[0]]; // Only allow one file for single operations
        } else {
            this.files[type] = [...this.files[type], ...files]; // Allow multiple for batch
        }
        this.updateFileList(type);
        this.updateButtonState(type);
    }

    updateFileList(type) {
        const listId = type === 'batchProtect' ? 'batchProtectFileList' :
                      type === 'batchVerify' ? 'batchVerifyFileList' :
                      `${type}FileList`;
        const fileList = document.getElementById(listId);

        if (!fileList) {
            console.warn(`File list element not found: ${listId}`);
            return;
        }

        fileList.innerHTML = '';
        fileList.style.display = this.files[type].length > 0 ? 'block' : 'none';

        this.files[type].forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">
                        <i class="fas fa-file-${this.getFileIcon(file.type)}"></i>
                    </div>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${this.formatFileSize(file.size)}</p>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-secondary btn-sm" onclick="app.removeFile(${index}, '${type}')">
                        <i class="fas fa-trash"></i>
                        Remove
                    </button>
                </div>
            `;
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

    // ----------------------
    // Secret Data Validation
    // ----------------------
    validateSecretData(input) {
        if (!input) return { valid: true };

        if (input.length > 10000) {
            return { valid: false, reason: "Secret data too long. Maximum 10,000 characters allowed." };
        }

        const forbiddenPatterns = [
            /<script[\s\S]*?>[\s\S]*?<\/script>/i,
            /\b(onerror|onload)\s*=/i,
            /\b(eval|exec|document\.cookie)\b/i,
            /\b(powershell|cmd\.exe|bash|sh)\b/i,
            /(javascript:|vbscript:|data:text\/html)/i
        ];

        for (const pattern of forbiddenPatterns) {
            if (pattern.test(input)) {
                return { valid: false, reason: "Secret data contains potentially malicious code or patterns." };
            }
        }

        return { valid: true };
    }

    // ----------------------
    // API REQUEST METHOD
    // ----------------------
    async apiRequest(endpoint, formData, progressBarId, alertId, resultsId, _retried = false) {
        try {
            console.log(`Making API request to: ${this.baseURL}${endpoint}`);

            this.resetAlert(alertId);
            this.updateProgress(progressBarId, 10);
            this.toggleLoading(true);

            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: "POST",
                body: formData
            });

            console.log(`Response status: ${response.status}`);
            this.updateProgress(progressBarId, 60);  
          const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const textResponse = await response.text();
                console.warn('Non-JSON response detected.', { 
                    status: response.status,
                    contentType, 
                    url: response.url,
                    textResponse: textResponse?.slice(0, 200) 
                });
                
                // Fallback strategy: try common API bases if first attempt failed
                if (!_retried) {
                    const originalBase = this.baseURL;
                    const candidates = [];
                    // Try Netlify functions path
                    if (originalBase !== '/.netlify/functions/api') candidates.push('/.netlify/functions/api');
                    // Try /api with Netlify redirect
                    if (originalBase !== '/api') candidates.push('/api');
                    
                    for (const candidate of candidates) {
                        try {
                            console.log(`Trying fallback API base: ${candidate}`);
                            const healthUrl = `${candidate}/health`;
                            const healthResp = await fetch(healthUrl, { method: 'GET' });
                            const ct = healthResp.headers.get('content-type') || '';
                            if (ct.includes('application/json')) {
                                this.baseURL = candidate;
                                console.log('Successfully switched API base to', candidate);
                                // Retry original request once
                                return await this.apiRequest(endpoint, formData, progressBarId, alertId, resultsId, true);
                            }
                        } catch (e) {
                            console.log(`Fallback ${candidate} failed:`, e.message);
                        }
                    }
                }
                
                // If fallback failed or already retried, surface error
                let errorMessage = 'Server configuration error: API endpoint not responding correctly.';
                if (textResponse && textResponse.includes('<!DOCTYPE')) {
                    errorMessage = 'Server Error: Expected JSON but received HTML. The API endpoint may not be properly configured.';
                } else if (response.status === 404) {
                    errorMessage = 'API endpoint not found. Please check server deployment.';
                } else if (response.status >= 500) {
                    errorMessage = 'Server internal error. Please check server logs.';
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            this.updateProgress(progressBarId, 100);
            console.log('Parsed response data:', data);      
      if (data.success) {
                const successMessage = data.message || "Operation completed successfully.";
                this.showAlert('success', successMessage, alertId.replace('Alert', ''));

                if (resultsId) {
                    this.displayResults(resultsId, data);
                }

                if (data.file_data && data.file_name) {
                    this.downloadFile(data.file_data, data.file_name);
                } else if (data.batch_results) {
                    data.batch_results.forEach(r => {
                        const resultData = r.result || r;
                        if (resultData && resultData.file_data && resultData.file_name) {
                            this.downloadFile(resultData.file_data, resultData.file_name);
                        }
                    });
                }
            } else {
                const errorMessage = data.error || data.message || "An unknown error occurred.";
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

    // ----------------------
    // RESULTS DISPLAY METHOD
    // ----------------------
    displayResults(resultsId, data) {
        const results = document.getElementById(resultsId);
        if (!results) return;

        results.style.display = "block";
        results.innerHTML = "<h3>Results</h3>";

        if (data.batch_results) {
            data.batch_results.forEach(r => {
                const statusClass = r.status === 'success' ? 'status-success' : 'status-error';
                const verificationClass = r.is_verified ? 'status-success' : 'status-warning';

                results.innerHTML += `
                  <div class="result-item">
                    <h4>${r.file_name}</h4>
                    <p>Status: <span class="status-badge ${statusClass}">${r.status}</span></p>
                    ${r.status === 'success' ? `
                        <p>Verification: <span class="status-badge ${verificationClass}">
                            ${r.verification_status || (r.result && r.result.success ? 'Protected' : 'Failed')}
                        </span></p>
                        <p>Current Hash: ${r.current_hash || 'N/A'}</p>
                        <p>Stored Hash: ${(r.result && r.result.protected_hash) || 'N/A'}</p>
                        ${r.extracted_data ? `<p>Extracted Data: <textarea readonly class="form-control">${r.extracted_data}</textarea></p>` : ''}
                    ` : `<p>Error: ${r.error}</p>`}
                  </div>
                `;
            });
        } else {      
      const verificationClass = data.is_verified ? 'status-success' : 'status-warning';

            results.innerHTML += `
              <div class="result-item">
                <h4>${data.file_name || data.original_filename || 'Document'}</h4>
                 ${data.message ? `<p><strong>${data.message}</strong></p>` : ""}
                ${typeof data.is_verified !== "undefined" ? `<p>Status: <span class="status-badge ${verificationClass}">${data.is_verified ? 'VERIFIED' : 'TAMPERED / UNKNOWN'}</span></p>` : ""}
                <p>Original Hash: ${data.original_hash || 'N/A'}</p>
                <p>Protected Hash: ${data.protected_hash || data.current_hash || 'N/A'}</p>
                ${data.protection_date ? `<p>Protection Date: ${new Date(data.protection_date).toLocaleString()}</p>` : ""}
                ${data.extracted_data ? `<p><strong>Extracted Data:</strong><br><textarea class="form-control" readonly>${data.extracted_data}</textarea></p>` : ""}
              </div>
            `;
        }
    }

    downloadFile(base64Data, fileName) {
        try {
            const byteCharacters = atob(base64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            this.showAlert('info', `${fileName} has been downloaded.`, 'protect');
        } catch (e) {
            console.error("Download failed", e);
            this.showAlert('error', `Failed to initiate download for ${fileName}.`, 'protect');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }    showA
lert(type, message, context = '') {
        const alertId = context ? `${context}Alert` :
                       this.currentTab === 'batch' ? 'batchAlert' :
                       `${this.currentTab}Alert`;
        const alert = document.getElementById(alertId);

        if (!alert) {
            console.warn(`Alert element not found: ${alertId}`);
            return;
        }

        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' :
                              type === 'error' ? 'exclamation-circle' :
                              'info-circle'}"></i>
            ${message}
        `;
        alert.style.display = 'flex';

        setTimeout(() => {
            alert.style.display = 'none';
        }, 6000);
    }

    showProgress(type, show = true) {
        const progressId = type === 'batchProtect' ? 'batchProtectProgress' :
                          type === 'batchVerify' ? 'batchVerifyProgress' :
                          `${type}Progress`;
        const progress = document.getElementById(progressId);

        if (progress) {
            progress.style.display = show ? 'block' : 'none';
            if (!show) {
                const progressBar = progress.querySelector('.progress-bar');
                if (progressBar) progressBar.style.width = '0%';
            }
        }
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
            progressBar.style.width = `${percent}%`;
        }
    }

    toggleLoading(show) {
        const loading = document.getElementById("loading");
        const content = document.querySelector('.content');
        if (loading && content) {
            loading.style.display = show ? "block" : "none";
            content.style.display = show ? "none" : "block";
        }
    }    a
sync protectDocuments() {
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

        formData.append("file", file);
        formData.append("secret_data", secretData);
        formData.append("encrypt_payload", String(encrypt));
        if (encrypt && password) formData.append("password", password);

        await this.apiRequest("/protect", formData, "protectProgressBar", "protectAlert", "protectResults");
    }

    async verifyDocuments() {
        if (this.files.verify.length === 0) {
            this.showAlert('error', "Please select a file to verify.", 'verify');
            return;
        }

        const formData = new FormData();
        formData.append("file", this.files.verify[0]);

        await this.apiRequest("/verify", formData, "verifyProgressBar", "verifyAlert", "verifyResults");
    }

    async extractData() {
        if (this.files.extract.length === 0) {
            this.showAlert('error', "Please select a file to extract data from.", 'extract');
            return;
        }

        const formData = new FormData();
        const password = prompt("Enter password if the data is encrypted, otherwise leave blank:");
        formData.append("file", this.files.extract[0]);
        if (password) {
            formData.append("password", password);
        }

        await this.apiRequest("/extract", formData, "extractProgressBar", "extractAlert", "extractResults");
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

        files.forEach(f => formData.append("file", f));
        formData.append("secret_data", secretData);
        formData.append("encrypt_payload", String(encrypt));
        if (encrypt && password) formData.append("password", password);

        await this.apiRequest("/batch-protect", formData, "batchProtectProgressBar", "batchAlert", "batchResults");
    }

    async batchVerifyDocuments() {
        if (this.files.batchVerify.length === 0) {
            this.showAlert('error', "Please select files for batch verification", 'batch');
            return;
        }

        const formData = new FormData();
        this.files.batchVerify.forEach(f => formData.append("file", f));

        await this.apiRequest("/batch-verify", formData, "batchVerifyProgressBar", "batchAlert", "batchResults");
    }

    // Hash Management Methods
    async loadHashManagementData() {
        if (this.currentTab === 'hashes') {
            await Promise.all([
                this.loadHashStats(),
                this.loadSyncStatus(),
                this.loadRecentHashes()
            ]);
        }
    }

    async loadHashStats() {
        const statsDiv = document.getElementById('hashStats');
        if (!statsDiv) return;

        try {
            const response = await fetch(`${this.baseURL}/hash/stats`);
            if (response.ok) {
                const data = await response.json();
                statsDiv.innerHTML = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <strong>Total Hashes:</strong><br>
                            <span style="font-size: 1.5rem; color: #667eea;">${data.total_hashes || 0}</span>
                        </div>
                        <div>
                            <strong>Synced:</strong><br>
                            <span style="font-size: 1.5rem; color: #28a745;">${data.synced_hashes || 0}</span>
                        </div>
                        <div>
                            <strong>Pending:</strong><br>
                            <span style="font-size: 1.5rem; color: #ffc107;">${data.pending_hashes || 0}</span>
                        </div>
                        <div>
                            <strong>Storage:</strong><br>
                            <span style="font-size: 1rem; color: #666;">${data.storage_size || '0 KB'}</span>
                        </div>
                    </div>
                `;
            } else {
                statsDiv.innerHTML = '<p style="color: #dc3545;">Failed to load statistics</p>';
            }
        } catch (error) {
            console.error('Failed to load hash stats:', error);
            statsDiv.innerHTML = '<p style="color: #dc3545;">Error loading statistics</p>';
        }
    } 
   async loadSyncStatus() {
        const syncDiv = document.getElementById('syncStatus');
        if (!syncDiv) return;

        try {
            const response = await fetch(`${this.baseURL}/hash/sync/status`);
            if (response.ok) {
                const data = await response.json();
                const lastSync = data.last_sync ? new Date(data.last_sync).toLocaleString() : 'Never';
                const statusColor = data.sync_enabled ? '#28a745' : '#6c757d';
                
                syncDiv.innerHTML = `
                    <div>
                        <p><strong>Status:</strong> 
                            <span style="color: ${statusColor};">
                                ${data.sync_enabled ? '✅ Enabled' : '⏸️ Disabled'}
                            </span>
                        </p>
                        <p><strong>Last Sync:</strong> ${lastSync}</p>
                        <p><strong>Pending Operations:</strong> ${data.pending_operations || 0}</p>
                        ${data.last_error ? `<p style="color: #dc3545;"><strong>Last Error:</strong> ${data.last_error}</p>` : ''}
                    </div>
                `;
            } else {
                syncDiv.innerHTML = '<p style="color: #dc3545;">Failed to load sync status</p>';
            }
        } catch (error) {
            console.error('Failed to load sync status:', error);
            syncDiv.innerHTML = '<p style="color: #dc3545;">Error loading sync status</p>';
        }
    }

    async loadRecentHashes() {
        const recentDiv = document.getElementById('recentHashes');
        if (!recentDiv) return;

        try {
            const response = await fetch(`${this.baseURL}/hash/list?limit=5`);
            if (response.ok) {
                const data = await response.json();
                if (data.hashes && data.hashes.length > 0) {
                    recentDiv.innerHTML = data.hashes.map(hash => `
                        <div style="padding: 8px; border-bottom: 1px solid #eee; font-size: 0.9rem;">
                            <div style="font-weight: 500; color: #333;">${hash.filename || 'Unknown'}</div>
                            <div style="color: #666; font-size: 0.8rem;">${hash.hash.substring(0, 16)}...</div>
                            <div style="color: #999; font-size: 0.8rem;">${new Date(hash.created_at).toLocaleDateString()}</div>
                        </div>
                    `).join('');
                } else {
                    recentDiv.innerHTML = '<p style="color: #666; text-align: center;">No hashes found</p>';
                }
            } else {
                recentDiv.innerHTML = '<p style="color: #dc3545;">Failed to load recent hashes</p>';
            }
        } catch (error) {
            console.error('Failed to load recent hashes:', error);
            recentDiv.innerHTML = '<p style="color: #dc3545;">Error loading recent hashes</p>';
        }
    }

    async syncAllHashes() {
        try {
            this.showAlert('info', 'Starting synchronization...', 'hashes');
            const response = await fetch(`${this.baseURL}/hash/sync/all`, { method: 'POST' });
            
            if (response.ok) {
                const data = await response.json();
                this.showAlert('success', `Synchronized ${data.synced_count || 0} hashes`, 'hashes');
                
                // Refresh status after a delay
                setTimeout(() => {
                    this.loadSyncStatus();
                    this.loadHashStats();
                }, 2000);
            } else {
                this.showAlert('error', 'Synchronization failed', 'hashes');
            }
        } catch (error) {
            console.error('Sync failed:', error);
            this.showAlert('error', 'Synchronization error: ' + error.message, 'hashes');
        }
    }    as
ync viewAllHashes() {
        try {
            const response = await fetch(`${this.baseURL}/hash/list?limit=100`);
            if (response.ok) {
                const data = await response.json();
                const modal = document.getElementById('hashListModal');
                const content = document.getElementById('hashListContent');
                
                if (data.hashes && data.hashes.length > 0) {
                    content.innerHTML = `
                        <div style="max-height: 400px; overflow-y: auto;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f8f9fa;">
                                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #dee2e6;">File</th>
                                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #dee2e6;">Hash</th>
                                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #dee2e6;">Date</th>
                                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #dee2e6;">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.hashes.map(hash => `
                                        <tr>
                                            <td style="padding: 8px; border-bottom: 1px solid #eee;">${hash.filename || 'Unknown'}</td>
                                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-family: monospace; font-size: 0.8rem;">${hash.hash.substring(0, 20)}...</td>
                                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-size: 0.9rem;">${new Date(hash.created_at).toLocaleDateString()}</td>
                                            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                                                <span style="color: ${hash.synced ? '#28a745' : '#ffc107'};">
                                                    ${hash.synced ? '✅ Synced' : '⏳ Pending'}
                                                </span>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                } else {
                    content.innerHTML = '<p style="text-align: center; color: #666;">No hash records found</p>';
                }
                
                modal.style.display = 'block';
            } else {
                this.showAlert('error', 'Failed to load hash list', 'hashes');
            }
        } catch (error) {
            console.error('Failed to load hash list:', error);
            this.showAlert('error', 'Error loading hash list: ' + error.message, 'hashes');
        }
    }

    async exportHashes() {
        try {
            this.showAlert('info', 'Preparing export...', 'hashes');
            const response = await fetch(`${this.baseURL}/hash/export`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `hash_export_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                this.showAlert('success', 'Hash export downloaded', 'hashes');
            } else {
                this.showAlert('error', 'Export failed', 'hashes');
            }
        } catch (error) {
            console.error('Export failed:', error);
            this.showAlert('error', 'Export error: ' + error.message, 'hashes');
        }
    } 
   async cleanupOldHashes() {
        try {
            const days = document.getElementById('cleanupDays').value;
            if (!days || days < 1) {
                this.showAlert('error', 'Please enter a valid number of days', 'hashes');
                return;
            }

            const response = await fetch(`${this.baseURL}/hash/cleanup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ days: parseInt(days) })
            });

            if (response.ok) {
                const data = await response.json();
                this.showAlert('success', `Cleaned up ${data.deleted_count} old records`, 'hashes');
                this.loadHashStats();
                this.loadRecentHashes();
            } else {
                this.showAlert('error', 'Cleanup failed', 'hashes');
            }
        } catch (error) {
            console.error('Cleanup failed:', error);
            this.showAlert('error', 'Cleanup error: ' + error.message, 'hashes');
        }
    }

    async syncPendingOperations() {
        if (this.pendingOperations.length === 0) return;

        try {
            // Attempt to sync pending operations
            await this.syncAllHashes();
            this.pendingOperations = [];
        } catch (error) {
            console.error('Failed to sync pending operations:', error);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentApp();
});