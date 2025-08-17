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
        this.baseURL = window.location.origin; // Automatically detect base URL
        this.init();
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
        this.files[type] = [...this.files[type], ...files];
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
    // Secret Data Validation
    // ----------------------
    validateSecretData(input) {
        if (!input) return { valid: true };

        // Limit size
        if (input.length > 10000) {
            return { valid: false, reason: "Secret data too long. Maximum 10,000 characters allowed." };
        }

        // Disallow scripts/macros/urls/commands
        const forbiddenPatterns = [
            /<script.*?>.*?<\/script>/is,   // HTML/JS scripts
            /\b(eval|exec|alert|onerror|onload|document\.cookie)\b/i, // JS injection
            /\b(powershell|cmd\.exe|bash|sh|wget|curl)\b/i,  // Command injection
            /\b(DROP\s+TABLE|ALTER\s+TABLE|INSERT\s+INTO|SELECT\s+\*)\b/i, // SQL injection
            /\b(macro|AutoOpen|ThisDocument|Shell\()?\b/i,  // Office macros
            /(http|https|ftp):\/\//i  // URLs
        ];

        for (const pattern of forbiddenPatterns) {
            if (pattern.test(input)) {
                return { valid: false, reason: "Secret data contains potentially malicious code or patterns." };
            }
        }

        return { valid: true };
    }

    // ----------------------
    // ENHANCED API REQUEST METHOD WITH PROPER ERROR HANDLING
    // ----------------------
    async apiRequest(endpoint, formData, progressBarId, alertId, resultsId) {
        try {
            console.log(`Making API request to: ${endpoint}`);
            
            this.resetAlert(alertId);
            this.updateProgress(progressBarId, 10);
            this.toggleLoading(true);

            const response = await fetch(endpoint, {
                method: "POST",
                body: formData
            });

            console.log(`Response status: ${response.status}`);
            console.log(`Response headers:`, response.headers);

            this.updateProgress(progressBarId, 60);

            // Check if response is HTML (error page) instead of JSON
            const contentType = response.headers.get('content-type');
            console.log(`Content-Type: ${contentType}`);

            if (!contentType || !contentType.includes('application/json')) {
                const textResponse = await response.text();
                console.error('Server returned non-JSON response:', textResponse);
                
                // Try to extract error message from HTML if possible
                let errorMessage = 'Server returned an invalid response';
                if (textResponse.includes('<!DOCTYPE')) {
                    errorMessage = 'Server error: Expected JSON but received HTML. Check server configuration.';
                } else if (textResponse.trim()) {
                    errorMessage = textResponse.trim();
                }
                
                throw new Error(errorMessage);
            }

            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                console.error('Failed to parse JSON response:', jsonError);
                const textResponse = await response.text();
                console.error('Raw response:', textResponse);
                throw new Error('Invalid JSON response from server');
            }

            this.updateProgress(progressBarId, 100);

            console.log('Parsed response data:', data);

            // Check for success in response
            const isSuccess = response.ok && (
                data.success === true || 
                data.batch_results !== undefined || 
                data.is_verified !== undefined
            );

            if (isSuccess) {
                const successMessage = data.message || "Operation completed successfully.";
                this.showAlert('success', successMessage, alertId.replace('Alert', ''));

                if (resultsId) {
                    this.displayResults(resultsId, data);
                }

                // NEW: Handle single or batch file downloads
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
            const errorMessage = err.message || "Request failed: Unknown error";
            this.showAlert('error', errorMessage, alertId.replace('Alert', ''));
        } finally {
            this.toggleLoading(false);
            setTimeout(() => this.updateProgress(progressBarId, 0), 1000);
        }
    }

    // ----------------------
    // ENHANCED RESULTS DISPLAY METHOD
    // ----------------------
    displayResults(resultsId, data) {
        const results = document.getElementById(resultsId);
        if (!results) return;

        results.style.display = "block";
        results.innerHTML = "<h3>Results</h3>";

        if (data.batch_results) {
            // Batch results
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
                        <p>Stored Hash: ${r.stored_hash || (r.result && r.result.protected_hash) || 'N/A'}</p>
                        ${r.extracted_data ? `<p>Extracted Data: <textarea readonly class="form-control">${r.extracted_data}</textarea></p>` : ''}
                    ` : `<p>Error: ${r.error}</p>`}
                  </div>
                `;
            });
        } else {
            // Single-file results
            const verificationClass = data.is_verified ? 'status-success' : 'status-warning';
            
            results.innerHTML += `
              <div class="result-item">
                <h4>${data.file_name || 'Document'}</h4>
                <p>Method: ${data.method || 'N/A'}</p>
                <p>Original Hash: ${data.original_hash || (data.metadata && data.metadata.original_hash) || 'N/A'}</p>
                <p>Protected Hash: ${data.protected_hash || (data.metadata && data.metadata.protected_hash) || 'N/A'}</p>
                ${data.current_hash ? `<p>Current Hash: ${data.current_hash}</p>` : ""}
                ${data.stored_hash ? `<p>Stored Hash: ${data.stored_hash}</p>` : ""}
                ${data.extracted_data ? `<p><strong>Extracted Data:</strong><br><textarea class="form-control" readonly>${data.extracted_data}</textarea></p>` : ""}
                ${typeof data.is_verified !== "undefined" ? `<p>Status: <span class="status-badge ${verificationClass}">${data.is_verified ? 'VERIFIED' : 'TAMPERED'}</span></p>` : ""}
                ${data.output_path ? `<p>Status: <span class="status-badge status-success">SAVED</span></p><p>Saved To: ${data.output_path}</p>` : ""}
              </div>
            `;
        }
    }

    // ----------------------
    // NEW: FILE DOWNLOAD HANDLER
    // ----------------------
    downloadFile(base64Data, fileName) {
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
        this.showAlert('success', `${fileName} is ready for download.`, 'protect');
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
        }, 5000);
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

    updateProgress(type, percent) {
        const progressId = type === 'batchProtect' ? 'batchProtectProgressBar' :
                          type === 'batchVerify' ? 'batchVerifyProgressBar' :
                          `${type}ProgressBar`;
        const progressBar = document.getElementById(progressId);

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }
    }

    toggleLoading(show) {
        const loader = document.getElementById("loading");
        if (loader) {
            loader.style.display = show ? "flex" : "none";
        }
    }

    // ----------------------
    // FIXED DOCUMENT OPERATIONS WITH PROPER ERROR HANDLING
    // ----------------------
    async protectDocuments() {
        const secretData = document.getElementById("secretData").value.trim();
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
        if (secretData) formData.append("secret_data", secretData);
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

        console.log('Starting document verification...');
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

        console.log('Starting data extraction...');
        await this.apiRequest("/extract", formData, "extractProgressBar", "extractAlert", "extractResults");
    }

    async batchProtectDocuments() {
        const secretData = document.getElementById("batchSecretData").value.trim();
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
        if (secretData) formData.append("secret_data", secretData);
        formData.append("encrypt_payload", String(encrypt));
        if (encrypt && password) formData.append("password", password);

        console.log(`Batch protecting ${files.length} documents...`);
        await this.apiRequest("/batch-protect", formData, "batchProtectProgressBar", "batchAlert", "batchResults");
    }

    async batchVerifyDocuments() {
        if (this.files.batchVerify.length === 0) {
            this.showAlert('error', "Please select files for batch verification", 'batch');
            return;
        }

        const formData = new FormData();
        this.files.batchVerify.forEach(f => formData.append("file", f));
        
        console.log('Starting batch verification...');
        await this.apiRequest("/batch-verify", formData, "batchVerifyProgressBar", "batchAlert", "batchResults");
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentApp();
});