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
        this.init();
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
            return '';
        }
    }

    init() {
        this.setupTabs();
        this.setupFileUploads();
        this.setupButtons();
        this.setupDragAndDrop();
        this.setupEncryptionToggles();
    }

    setupTabs() {
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
                document.getElementById(tabId).classList.add('active');

                this.currentTab = tabId;
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
        this.addFiles(files, type);
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

        if (!fileList) return;

        fileList.innerHTML = '';

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
    // Secret Data Validation (FIXED)
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
    async apiRequest(endpoint, formData, progressBarId, alertId, resultsId) {
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
                console.error('Server returned non-JSON response:', textResponse);
                let errorMessage = 'Server returned an invalid response. Check server logs.';
                if (textResponse.includes('<!DOCTYPE')) {
                    errorMessage = 'Server Error: Expected JSON but received HTML. Check server configuration.';
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
    }

    showAlert(type, message, context = '') {
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
    }

    async protectDocuments() {
        const secretData = document.getElementById("secretData").value; // Don't trim, preserve user spaces
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
        formData.append("secret_data", secretData); // Always send, even if empty
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentApp();
});