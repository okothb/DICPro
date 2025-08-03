// DocProject Web Application JavaScript
// Handles file uploads, API interactions, and UI management

class DocProjectWebApp {
    constructor() {
        // Use relative URLs for Netlify deployment, fallback to localhost for development
        this.apiBaseUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        this.files = {
            protect: [],
            verify: [],
            extract: [],
            batch: []
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.updateStatus('Ready');
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // File input changes
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleFileSelect(e);
            });
        });

        // Upload area clicks
        document.querySelectorAll('.upload-area').forEach(area => {
            area.addEventListener('click', (e) => {
                const fileInput = area.querySelector('input[type="file"]');
                if (fileInput) {
                    fileInput.click();
                }
            });
        });

        // Checkbox interactions
        document.getElementById('encrypt-payload').addEventListener('change', (e) => {
            this.togglePasswordField('password-group', e.target.checked);
        });

        document.getElementById('batch-encrypt-payload').addEventListener('change', (e) => {
            this.togglePasswordField('batch-password-group', e.target.checked);
        });

        // Output folder browse buttons - show help dialog
        document.getElementById('browse-output-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showFolderHelpDialog();
        });

        document.getElementById('batch-browse-output-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showFolderHelpDialog();
        });

        // Add validation for manual folder path input
        document.getElementById('output-folder').addEventListener('input', (e) => {
            const folderPath = e.target.value.trim();
            const validation = this.validateOutputFolder(folderPath);
            this.setFolderInputStatus('output-folder', validation.isValid, validation.message);
        });

        document.getElementById('batch-output-folder').addEventListener('input', (e) => {
            const folderPath = e.target.value.trim();
            const validation = this.validateOutputFolder(folderPath);
            this.setFolderInputStatus('batch-output-folder', validation.isValid, validation.message);
        });

        // Form submissions
        document.getElementById('protect-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.protectDocuments();
        });

        document.getElementById('verify-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.verifyDocuments();
        });

        document.getElementById('extract-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.extractData();
        });

        document.getElementById('batch-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.processBatch();
        });

        // Batch operation type selection
        document.querySelectorAll('input[name="batch-operation"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.toggleBatchOperationFields(e.target.value);
            });
        });
    }

    setupDragAndDrop() {
        document.querySelectorAll('.upload-area').forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                const files = Array.from(e.dataTransfer.files);
                const tabType = this.getTabTypeFromArea(area);
                this.addFiles(tabType, files);
            });
        });
    }

    getTabTypeFromArea(area) {
        const areaId = area.id;
        if (areaId.includes('protect')) return 'protect';
        if (areaId.includes('verify')) return 'verify';
        if (areaId.includes('extract')) return 'extract';
        if (areaId.includes('batch')) return 'batch';
        return 'protect';
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.updateStatus(`Switched to ${tabName} tab`);
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        const tabType = this.getTabTypeFromInput(event.target);
        this.addFiles(tabType, files);
    }

    getTabTypeFromInput(input) {
        const inputId = input.id;
        if (inputId.includes('protect')) return 'protect';
        if (inputId.includes('verify')) return 'verify';
        if (inputId.includes('extract')) return 'extract';
        if (inputId.includes('batch')) return 'batch';
        return 'protect';
    }

    addFiles(tabType, files) {
        files.forEach(file => {
            // Check if file is already added
            const existingFile = this.files[tabType].find(f => f.name === file.name && f.size === file.size);
            if (!existingFile) {
                this.files[tabType].push(file);
            }
        });

        this.updateFileList(tabType);
        this.updateStatus(`Added ${files.length} file(s) to ${tabType} tab`);
    }

    updateFileList(tabType) {
        const fileList = document.getElementById(`${tabType}-file-list`);
        fileList.innerHTML = '';

        this.files[tabType].forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-file"></i>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">(${this.formatFileSize(file.size)})</span>
                </div>
                <button class="remove-btn" onclick="app.removeFile('${tabType}', ${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            fileList.appendChild(fileItem);
        });
    }

    removeFile(tabType, index) {
        this.files[tabType].splice(index, 1);
        this.updateFileList(tabType);
        this.updateStatus(`Removed file from ${tabType} tab`);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    togglePasswordField(fieldId, show) {
        const field = document.getElementById(fieldId);
        if (show) {
            field.style.display = 'block';
        } else {
            field.style.display = 'none';
            field.querySelector('input').value = '';
        }
    }

    showLoading(message = 'Processing...') {
        document.getElementById('loading-message').textContent = message;
        document.getElementById('loading-modal').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading-modal').style.display = 'none';
    }

    updateStatus(message) {
        document.getElementById('status-text').textContent = message;
    }

    updateProgress(percent) {
        const progressBar = document.getElementById('progress-bar');
        const progressFill = document.getElementById('progress-fill');
        
        if (percent > 0) {
            progressBar.style.display = 'block';
            progressFill.style.width = `${percent}%`;
        } else {
            progressBar.style.display = 'none';
        }
    }

    validateOutputFolder(folderPath) {
        if (!folderPath || folderPath.trim() === '') {
            return { isValid: false, message: 'Output folder path is required. Enter the full path to your output folder.' };
        }
        
        // Basic validation - check if it looks like a valid path
        if (folderPath.includes('..') || folderPath.includes('//')) {
            return { isValid: false, message: 'Invalid folder path detected.' };
        }
        
        // Check for common path patterns
        const trimmedPath = folderPath.trim();
        if (trimmedPath.length < 3) {
            return { isValid: false, message: 'Path too short. Please enter a valid folder path.' };
        }
        
        return { isValid: true, message: 'Output folder path is valid.' };
    }

    showFolderHelpDialog() {
        const helpText = `
            <div style="padding: 20px;">
                <h3 style="margin-bottom: 15px; color: #333;">How to Set Output Folder</h3>
                <p style="margin-bottom: 10px; color: #666;">
                    Since this is a web application, you need to manually enter the full path to the folder where you want the protected files to be saved.
                </p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="margin-bottom: 10px; color: #333;">Examples:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666;">
                        <li><strong>Windows:</strong> C:\\Users\\YourName\\Documents\\Output</li>
                        <li><strong>Mac:</strong> /Users/YourName/Documents/Output</li>
                        <li><strong>Linux:</strong> /home/username/documents/output</li>
                    </ul>
                </div>
                <p style="margin-top: 15px; color: #666; font-size: 0.9em;">
                    <strong>Note:</strong> The folder must exist on your computer and be accessible by the application.
                </p>
            </div>
        `;
        
        // Create a modal dialog
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        `;
        
        modalContent.innerHTML = helpText;
        
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.cssText = `
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin: 20px;
            font-size: 14px;
        `;
        closeButton.onclick = () => {
            document.body.removeChild(modal);
        };
        
        modalContent.appendChild(closeButton);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // Close on background click
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
    }

    toggleBatchOperationFields(operationType) {
        const protectionFields = document.getElementById('batch-protection-fields');
        const verificationFields = document.getElementById('batch-verification-fields');
        const batchBtn = document.getElementById('batch-btn');
        
        if (operationType === 'protect') {
            protectionFields.style.display = 'block';
            verificationFields.style.display = 'none';
            batchBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Process Batch Protection';
        } else {
            protectionFields.style.display = 'none';
            verificationFields.style.display = 'block';
            batchBtn.innerHTML = '<i class="fas fa-check-circle"></i> Process Batch Verification';
        }
    }

    setFolderInputStatus(inputId, isValid, message) {
        const input = document.getElementById(inputId);
        const formGroup = input.closest('.form-group');
        
        // Remove existing status classes
        formGroup.classList.remove('valid', 'invalid');
        
        // Add appropriate class
        if (isValid) {
            formGroup.classList.add('valid');
        } else {
            formGroup.classList.add('invalid');
        }
        
        // Update status message if there's a small element
        const smallElement = formGroup.querySelector('small');
        if (smallElement) {
            smallElement.textContent = message;
            smallElement.style.color = isValid ? '#28a745' : '#dc3545';
        }
    }

    validateSecretData(secretData) {
        // Check for empty data
        if (!secretData) {
            return {
                isValid: false,
                error: "Secret data cannot be empty."
            };
        }
        
        // Check for excessive whitespace (potential obfuscation)
        if (secretData.trim().length === 0) {
            return {
                isValid: false,
                error: "Secret data cannot be empty or contain only whitespace."
            };
        }
        
        // Check length limits
        if (secretData.length > 10000) {
            return {
                isValid: false,
                error: "Secret data is too long. Maximum allowed length is 10,000 characters."
            };
        }
        
        // Define allowed characters: letters, numbers, spaces, and common punctuation
        const allowedChars = /^[a-zA-Z0-9\s.,!?;:()\[\]{}"'\-_@#$%&*+=<>/~]*$/;
        
        // Patterns that indicate potentially malicious content
        const maliciousPatterns = [
            /<script[^>]*>.*?<\/script>/gi,
            /javascript:/gi,
            /vbscript:/gi,
            /data:text\/html/gi,
            /data:application\/x-javascript/gi,
            /(cmd|powershell|bash|sh)\s+\/[ck]/gi,
            /exec\s*\(/gi,
            /eval\s*\(/gi,
            /system\s*\(/gi,
            /(http|https|ftp):\/\//gi,
            /file:\/\//gi,
            /\\\\([a-zA-Z0-9\-\.]+)\\/gi,
            /(union|select|insert|update|delete|drop|create|alter)\s+/gi,
            /--\s*$/gm,
            /\/\*.*?\*\//gs,
            /on\w+\s*=/gi,
            /<iframe/gi,
            /<object/gi,
            /<embed/gi,
            /^MZ\s*/gi,
            /^PE\s*/gi,
            /^ELF\s*/gi
        ];
        
        // Check for malicious patterns
        for (const pattern of maliciousPatterns) {
            if (pattern.test(secretData)) {
                return {
                    isValid: false,
                    error: `Contains potentially malicious content: ${pattern.source}`
                };
            }
        }
        
        // Check for disallowed characters
        if (!allowedChars.test(secretData)) {
            const disallowedChars = secretData.split('').filter(char => !allowedChars.test(char));
            return {
                isValid: false,
                error: `Contains disallowed characters: ${[...new Set(disallowedChars)].join('')}`
            };
        }
        
        return { isValid: true, error: "" };
    }

    async makeApiCall(endpoint, formData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    async protectDocuments() {
        if (this.files.protect.length === 0) {
            this.showError('Please select at least one file to protect.');
            return;
        }

        const secretData = document.getElementById('secret-data').value.trim();
        if (!secretData) {
            this.showError('Please enter secret data to embed.');
            return;
        }
        
        // Validate secret data for security
        const validationResult = this.validateSecretData(secretData);
        if (!validationResult.isValid) {
            this.showError(`Secret data validation failed: ${validationResult.error}`);
            return;
        }

        const encryptPayload = document.getElementById('encrypt-payload').checked;
        const password = document.getElementById('password').value;
        const outputFolder = document.getElementById('output-folder').value.trim();
        const folderValidation = this.validateOutputFolder(outputFolder);

        if (!folderValidation.isValid) {
            this.showError(folderValidation.message);
            return;
        }

        if (encryptPayload && !password) {
            this.showError('Please enter an encryption password.');
            return;
        }

        this.showLoading('Protecting documents...');
        this.updateProgress(10);

        try {
            const formData = new FormData();
            formData.append('secret_data', secretData);
            formData.append('encrypt_payload', encryptPayload);
            if (password) {
                formData.append('password', password);
            }
            formData.append('output_folder', outputFolder);

            // Add files
            this.files.protect.forEach(file => {
                formData.append('file', file);
            });

            this.updateProgress(30);
            const result = await this.makeApiCall('/protect', formData);
            this.updateProgress(90);

            this.displayProtectResults(result);
            this.updateProgress(100);
            this.updateStatus('Documents protected successfully');

        } catch (error) {
            this.showError(`Failed to protect documents: ${error.message}`);
        } finally {
            this.hideLoading();
            this.updateProgress(0);
        }
    }

    async verifyDocuments() {
        if (this.files.verify.length === 0) {
            this.showError('Please select at least one file to verify.');
            return;
        }

        this.showLoading('Verifying documents...');
        this.updateProgress(10);

        try {
            const formData = new FormData();
            this.files.verify.forEach(file => {
                formData.append('file', file);
            });

            this.updateProgress(30);
            const result = await this.makeApiCall('/verify', formData);
            this.updateProgress(90);

            this.displayVerifyResults(result);
            this.updateProgress(100);
            this.updateStatus('Documents verified successfully');

        } catch (error) {
            this.showError(`Failed to verify documents: ${error.message}`);
        } finally {
            this.hideLoading();
            this.updateProgress(0);
        }
    }

    async extractData() {
        if (this.files.extract.length === 0) {
            this.showError('Please select at least one file to extract data from.');
            return;
        }

        this.showLoading('Extracting data...');
        this.updateProgress(10);

        try {
            const formData = new FormData();
            this.files.extract.forEach(file => {
                formData.append('file', file);
            });

            this.updateProgress(30);
            const result = await this.makeApiCall('/extract', formData);
            this.updateProgress(90);

            this.displayExtractResults(result);
            this.updateProgress(100);
            this.updateStatus('Data extracted successfully');

        } catch (error) {
            this.showError(`Failed to extract data: ${error.message}`);
        } finally {
            this.hideLoading();
            this.updateProgress(0);
        }
    }

    async processBatch() {
        if (this.files.batch.length === 0) {
            this.showError('Please select at least one file for batch processing.');
            return;
        }

        // Get the selected operation type
        const operationType = document.querySelector('input[name="batch-operation"]:checked').value;

        if (operationType === 'protect') {
            await this.processBatchProtection();
        } else {
            await this.processBatchVerification();
        }
    }

    async processBatchProtection() {
        const secretData = document.getElementById('batch-secret-data').value.trim();
        if (!secretData) {
            this.showError('Please enter secret data to embed.');
            return;
        }
        
        // Validate secret data for security
        const validationResult = this.validateSecretData(secretData);
        if (!validationResult.isValid) {
            this.showError(`Secret data validation failed: ${validationResult.error}`);
            return;
        }

        const encryptPayload = document.getElementById('batch-encrypt-payload').checked;
        const password = document.getElementById('batch-password').value;
        const outputFolder = document.getElementById('batch-output-folder').value.trim();
        const folderValidation = this.validateOutputFolder(outputFolder);

        if (!folderValidation.isValid) {
            this.showError(folderValidation.message);
            return;
        }

        if (encryptPayload && !password) {
            this.showError('Please enter an encryption password.');
            return;
        }

        this.showLoading('Processing batch protection...');
        this.updateProgress(10);

        try {
            const formData = new FormData();
            formData.append('secret_data', secretData);
            formData.append('encrypt_payload', encryptPayload);
            if (password) {
                formData.append('password', password);
            }
            formData.append('output_folder', outputFolder);

            // Add files
            this.files.batch.forEach(file => {
                formData.append('files', file);
            });

            this.updateProgress(30);
            const result = await this.makeApiCall('/batch-protect', formData);
            this.updateProgress(90);

            this.displayBatchResults(result);
            this.updateProgress(100);
            this.updateStatus('Batch protection completed');

        } catch (error) {
            this.showError(`Failed to process batch protection: ${error.message}`);
        } finally {
            this.hideLoading();
            this.updateProgress(0);
        }
    }

    async processBatchVerification() {
        this.showLoading('Processing batch verification...');
        this.updateProgress(10);

        try {
            const formData = new FormData();

            // Add files
            this.files.batch.forEach(file => {
                formData.append('files', file);
            });

            this.updateProgress(30);
            const result = await this.makeApiCall('/batch-verify', formData);
            this.updateProgress(90);

            this.displayBatchResults(result);
            this.updateProgress(100);
            this.updateStatus('Batch verification completed');

        } catch (error) {
            this.showError(`Failed to process batch verification: ${error.message}`);
        } finally {
            this.hideLoading();
            this.updateProgress(0);
        }
    }

    displayProtectResults(result) {
        const resultsSection = document.getElementById('protect-results');
        const resultsList = document.getElementById('protect-results-list');
        
        resultsList.innerHTML = '';
        
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.success ? '' : 'error'}`;
        
        resultItem.innerHTML = `
            <h4>${result.success ? 'Success' : 'Error'}</h4>
            <p><strong>Message:</strong> ${result.message}</p>
            <p><strong>Original File:</strong> ${result.original_file}</p>
            <p><strong>Protected File:</strong> ${result.protected_file}</p>
            <p><strong>Method:</strong> ${result.method}</p>
            <p><strong>Original Hash:</strong> ${result.original_hash}</p>
            <p><strong>Protected Hash:</strong> ${result.protected_hash}</p>
            <p><strong>Processing Time:</strong> ${result.processing_time}s</p>
            <span class="status ${result.success ? 'success' : 'error'}">
                ${result.success ? 'SUCCESS' : 'ERROR'}
            </span>
        `;
        
        resultsList.appendChild(resultItem);
        resultsSection.style.display = 'block';
    }

    displayVerifyResults(result) {
        const resultsSection = document.getElementById('verify-results');
        const resultsList = document.getElementById('verify-results-list');
        
        resultsList.innerHTML = '';
        
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.success ? '' : 'error'}`;
        
        const verificationStatus = result.is_verified ? 'VERIFIED' : 'NOT VERIFIED';
        const statusClass = result.is_verified ? 'success' : 'error';
        
        resultItem.innerHTML = `
            <h4>${result.success ? 'Success' : 'Error'}</h4>
            <p><strong>Message:</strong> ${result.message}</p>
            <p><strong>File:</strong> ${result.file_path}</p>
            <p><strong>Status:</strong> <span class="status ${statusClass}">${verificationStatus}</span></p>
            <p><strong>Current Hash:</strong> ${result.current_hash}</p>
            <p><strong>Stored Hash:</strong> ${result.stored_hash}</p>
            ${result.extracted_data ? `<p><strong>Extracted Data:</strong> ${result.extracted_data}</p>` : ''}
            <span class="status ${result.success ? 'success' : 'error'}">
                ${result.success ? 'SUCCESS' : 'ERROR'}
            </span>
        `;
        
        resultsList.appendChild(resultItem);
        resultsSection.style.display = 'block';
    }

    displayExtractResults(result) {
        const resultsSection = document.getElementById('extract-results');
        const resultsList = document.getElementById('extract-results-list');
        
        resultsList.innerHTML = '';
        
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.success ? '' : 'error'}`;
        
        resultItem.innerHTML = `
            <h4>${result.success ? 'Success' : 'Error'}</h4>
            <p><strong>Message:</strong> ${result.message}</p>
            <p><strong>File:</strong> ${result.file_path}</p>
            <p><strong>Extracted Data:</strong> ${result.extracted_data || 'None'}</p>
            <p><strong>Hashes Match:</strong> ${result.hashes_match ? 'Yes' : 'No'}</p>
            <span class="status ${result.success ? 'success' : 'error'}">
                ${result.success ? 'SUCCESS' : 'ERROR'}
            </span>
        `;
        
        resultsList.appendChild(resultItem);
        resultsSection.style.display = 'block';
    }

    displayBatchResults(result) {
        const resultsSection = document.getElementById('batch-results');
        const resultsList = document.getElementById('batch-results-list');
        
        resultsList.innerHTML = '';
        
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.success ? '' : 'error'}`;
        
        resultItem.innerHTML = `
            <h4>${result.success ? 'Success' : 'Error'}</h4>
            <p><strong>Message:</strong> ${result.message}</p>
            <p><strong>Total Files:</strong> ${result.total_files}</p>
            <p><strong>Successful:</strong> ${result.successful}</p>
            <p><strong>Failed:</strong> ${result.failed}</p>
            <span class="status ${result.success ? 'success' : 'error'}">
                ${result.success ? 'SUCCESS' : 'ERROR'}
            </span>
        `;
        
        resultsList.appendChild(resultItem);
        resultsSection.style.display = 'block';
        
        // Display individual results if available
        if (result.results && result.results.length > 0) {
            result.results.forEach((item, index) => {
                const itemDiv = document.createElement('div');
                itemDiv.className = `result-item ${item.status === 'success' ? '' : 'error'}`;
                
                // Determine if this is a verification result
                const isVerification = item.hasOwnProperty('is_verified');
                
                itemDiv.innerHTML = `
                    <h5>${item.file}</h5>
                    <p><strong>Status:</strong> <span class="status ${item.status === 'success' ? 'success' : 'error'}">${item.status.toUpperCase()}</span></p>
                    ${isVerification ? `<p><strong>Verification:</strong> <span class="status ${item.is_verified ? 'success' : 'error'}">${item.is_verified ? 'VERIFIED' : 'NOT VERIFIED'}</span></p>` : ''}
                    ${item.protected_file ? `<p><strong>Protected File:</strong> ${item.protected_file}</p>` : ''}
                    ${item.method ? `<p><strong>Method:</strong> ${item.method}</p>` : ''}
                    ${item.original_hash ? `<p><strong>Original Hash:</strong> ${item.original_hash}</p>` : ''}
                    ${item.protected_hash ? `<p><strong>Protected Hash:</strong> ${item.protected_hash}</p>` : ''}
                    ${item.current_hash ? `<p><strong>Current Hash:</strong> ${item.current_hash}</p>` : ''}
                    ${item.stored_hash ? `<p><strong>Stored Hash:</strong> ${item.stored_hash}</p>` : ''}
                    ${item.extracted_data ? `<p><strong>Extracted Data:</strong> ${item.extracted_data}</p>` : ''}
                    ${item.error ? `<p><strong>Error:</strong> ${item.error}</p>` : ''}
                `;
                
                resultsList.appendChild(itemDiv);
            });
        }
    }

    showError(message) {
        this.updateStatus(`Error: ${message}`);
        // You could also show a toast notification here
        console.error(message);
    }

    // Health check method
    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                const health = await response.json();
                this.updateStatus(`API Status: ${health.status}`);
                return true;
            }
        } catch (error) {
            this.updateStatus('API not available');
            return false;
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocProjectWebApp();
    
    // Check API health on startup
    setTimeout(() => {
        app.checkApiHealth();
    }, 1000);
}); 