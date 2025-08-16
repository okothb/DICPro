// Document Security Suite - Frontend JavaScript
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
            file.type === 'application/pdf'
        );
        
        if (files.length > 0) {
            this.addFiles(files, type);
        } else {
            this.showAlert('error', 'Please drop only PDF files.', type);
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
                        <i class="fas fa-file-pdf"></i>
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
    // Validate Output Folder
    // ----------------------
    async validateOutputFolder(path) {
        if (!path) return path;
        
        const formData = new FormData();
        formData.append("path", path);

        try {
            const response = await fetch("/validate-path", { method: "POST", body: formData });
            const data = await response.json();
            return data.valid ? data.sanitized_path : null;
        } catch (err) {
            return null;
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
        
        if (!alert) return;

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
            loader.style.display = show ? "block" : "none";
        }
    }

    // ----------------------
    // API Request Wrapper
    // ----------------------
    async apiRequest(endpoint, formData, progressBarId, alertId, resultsId) {
        try {
            this.resetAlert(alertId);
            this.updateProgress(progressBarId, 10);
            this.toggleLoading(true);

            const response = await fetch(endpoint, {
                method: "POST",
                body: formData
            });

            this.updateProgress(progressBarId, 60);

            const data = await response.json();
            this.updateProgress(progressBarId, 100);

            if (data.success) {
                this.showAlert('success', data.message || "Success");

                if (resultsId) {
                    const results = document.getElementById(resultsId);
                    if (results) {
                        results.style.display = "block";
                        results.innerHTML = "";

                        if (data.results) {
                            // Batch results
                            data.results.forEach(r => {
                                results.innerHTML += `
                                  <div class="result-item">
                                    <h4>${r.file}</h4>
                                    <p>Status: <span class="status-badge ${r.status === 'success' ? 'status-success' : 'status-error'}">${r.status}</span></p>
                                    <p>Method: ${r.method || 'N/A'}</p>
                                    <p>Original Hash: ${r.original_hash || 'N/A'}</p>
                                    <p>Protected Hash: ${r.protected_hash || 'N/A'}</p>
                                    ${r.protected_file ? `<p>Saved To: ${r.protected_file}</p>` : ""}
                                  </div>
                                `;
                            });
                        } else {
                            // Single-file results
                            results.innerHTML = `
                              <div class="result-item">
                                <h4>${data.protected_file || data.file_path || data.original_file || 'Document'}</h4>
                                <p>Method: ${data.method || 'N/A'}</p>
                                <p>Original Hash: ${data.original_hash || 'N/A'}</p>
                                <p>Protected Hash: ${data.protected_hash || 'N/A'}</p>
                                ${data.current_hash ? `<p>Current Hash: ${data.current_hash}</p>` : ""}
                                ${data.stored_hash ? `<p>Stored Hash: ${data.stored_hash}</p>` : ""}
                                ${data.extracted_data ? `<p><strong>Extracted Data:</strong> ${data.extracted_data}</p>` : ""}
                                ${typeof data.is_verified !== "undefined" ? `<p>Status: <span class="status-badge ${data.is_verified ? 'status-success' : 'status-warning'}">${data.is_verified ? 'VERIFIED' : 'NOT VERIFIED'}</span></p>` : ""}
                                ${data.protected_file ? `<p>Status: <span class="status-badge status-success">SAVED</span></p>` : ""}
                                ${formData.get("output_folder") ? `<p>Saved To: ${formData.get("output_folder")}</p>` : ""}
                              </div>
                            `;
                        }
                    }
                }
            } else {
                this.showAlert('error', data.error || "An error occurred");
            }
        } catch (err) {
            this.showAlert('error', "Request failed: " + err.message);
        } finally {
            this.toggleLoading(false);
            setTimeout(() => this.updateProgress(progressBarId, 0), 1000);
        }
    }

    async protectDocuments() {
        const outputFolder = document.getElementById("outputFolder").value.trim();
        if (!outputFolder) {
            this.showAlert('error', "Output folder path is required", 'protect');
            return;
        }

        const validPath = await this.validateOutputFolder(outputFolder);
        if (!validPath) {
            this.showAlert('error', "Invalid output folder path", 'protect');
            return;
        }

        const secretData = document.getElementById("secretData").value;
        const validation = this.validateSecretData(secretData);
        if (!validation.valid) {
            this.showAlert('error', validation.reason, 'protect');
            return;
        }

        if (this.files.protect.length === 0) {
            this.showAlert('error', "Please select files to protect", 'protect');
            return;
        }

        const formData = new FormData();
        const files = this.files.protect;
        const secretFile = document.getElementById("secretFile").files[0];
        const encrypt = document.getElementById("encryptPayload").checked;
        const password = document.getElementById("encryptionPassword").value;

        Array.from(files).forEach(f => formData.append("file", f));
        if (secretData) formData.append("secret_data", secretData);
        if (secretFile) formData.append("secret_file", secretFile);
        formData.append("encrypt_payload", encrypt);
        if (encrypt && password) formData.append("password", password);
        formData.append("output_folder", validPath);

        await this.apiRequest("/protect", formData, "protectProgressBar", "protectAlert", "protectResults");
    }

    async verifyDocuments() {
        if (this.files.verify.length === 0) {
            this.showAlert('error', "Please select files to verify", 'verify');
            return;
        }

        const formData = new FormData();
        Array.from(this.files.verify).forEach(f => formData.append("file", f));
        
        await this.apiRequest("/verify", formData, "verifyProgressBar", "verifyAlert", "verifyResults");
    }

    async extractData() {
        if (this.files.extract.length === 0) {
            this.showAlert('error', "Please select files to extract data from", 'extract');
            return;
        }

        const formData = new FormData();
        Array.from(this.files.extract).forEach(f => formData.append("file", f));
        
        await this.apiRequest("/extract", formData, "extractProgressBar", "extractAlert", "extractResults");
    }

    async batchProtectDocuments() {
        const outputFolder = document.getElementById("batchOutputFolder").value.trim();
        if (!outputFolder) {
            this.showAlert('error', "Output folder path is required", 'batch');
            return;
        }

        const validPath = await this.validateOutputFolder(outputFolder);
        if (!validPath) {
            this.showAlert('error', "Invalid output folder path", 'batch');
            return;
        }

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

        Array.from(files).forEach(f => formData.append("file", f));
        if (secretData) formData.append("secret_data", secretData);
        formData.append("encrypt_payload", encrypt);
        if (encrypt && password) formData.append("password", password);
        formData.append("output_folder", validPath);

        await this.apiRequest("/batch-protect", formData, "batchProtectProgressBar", "batchAlert", "batchResults");
    }

    async batchVerifyDocuments() {
        if (this.files.batchVerify.length === 0) {
            this.showAlert('error', "Please select files for batch verification", 'batch');
            return;
        }

        const formData = new FormData();
        Array.from(this.files.batchVerify).forEach(f => formData.append("file", f));
        
        await this.apiRequest("/batch-verify", formData, "batchVerifyProgressBar", "batchAlert", "batchResults");
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentApp();
});