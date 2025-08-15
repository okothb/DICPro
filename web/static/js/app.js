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
        this.deviceInfo = this.detectDevice();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupDeviceDetection();
        this.setupSmartSuggestions();
        this.updateStatus('Ready');
    }

    setupEventListeners() {
        // Tab switching - Use event delegation for better performance
        document.querySelector('.tabs').addEventListener('click', (e) => {
            const tabBtn = e.target.closest('.tab-btn');
            if (tabBtn && tabBtn.dataset.tab) {
                e.preventDefault();
                this.switchTab(tabBtn.dataset.tab);
            }
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
            this.updateFolderStatus('output-folder', validation.isValid, validation.message);
        });

        document.getElementById('batch-output-folder').addEventListener('input', (e) => {
            const folderPath = e.target.value.trim();
            const validation = this.validateOutputFolder(folderPath);
            this.updateFolderStatus('batch-output-folder', validation.isValid, validation.message);
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
        try {
            // Update tab buttons
            const tabButtons = document.querySelectorAll('.tab-btn');
            tabButtons.forEach(btn => {
                if (btn.getAttribute('data-tab') === tabName) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            // Update tab content
            const tabPanes = document.querySelectorAll('.tab-pane');
            tabPanes.forEach(pane => {
                if (pane.id === tabName) {
                    pane.classList.add('active');
                } else {
                    pane.classList.remove('active');
                }
            });

            this.updateStatus(`Switched to ${tabName} tab`);
            return true;
        } catch (error) {
            console.error('Error switching tabs:', error);
            return false;
        }
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
        // Get OS or detect from path if not set
        const os = this.deviceInfo?.os || this.detectOSFromPath(folderPath || '');
        return this.validatePathForOS(folderPath || '', os);
    }
    
    detectOSFromPath(path) {
        if (!path) return 'unknown';
        if (/^[A-Za-z]:[\\/]/.test(path) || /^\\/.test(path)) return 'windows';
        if (path.startsWith('/Volumes/') || path.startsWith('/Users/')) return 'macos';
        if (path.startsWith('/storage/') || path.startsWith('/sdcard/')) return 'android';
        if (path.startsWith('/var/mobile/') || path.startsWith('/private/var/')) return 'ios';
        if (path.startsWith('/home/chronos/')) return 'chromeos';
        if (path.startsWith('/')) return 'linux';
        return 'unknown';
    }
    
    validatePathForOS(path, os) {
        if (!path || path.trim() === '') {
            return { 
                isValid: null, 
                message: 'Please enter a folder path',
                os: os
            };
        }
        
        const trimmedPath = path.trim();
        const result = { 
            isValid: false,
            message: '',
            os: os
        };
        
        // Check minimum length
        if (trimmedPath.length < 2) {
            result.isValid = false;
            result.message = 'Path too short. Please enter a valid folder path.';
            return result;
        }
        
        // Check for dangerous patterns
        if (trimmedPath.includes('..') || (trimmedPath.includes('//') && !trimmedPath.startsWith('//'))) {
            result.message = 'Invalid pattern detected. Avoid using ".." or multiple slashes except at the start of network paths.';
            result.isValid = false;
            return result;
        }
        
        // OS-specific validation
        switch (os) {
            case 'windows':
                result.isValid = /^[A-Za-z]:[\\/]/.test(trimmedPath) || /^\\\\[^\\/]+\\.*/.test(trimmedPath);
                result.message = result.isValid ? 'Windows path looks good!' : 
                    'Windows paths should start with a drive letter (e.g., C:\\\\) or network path (\\\\server\\\\)';
                
                if (result.isValid && /[<>:"|?*]/.test(trimmedPath)) {
                    result.isValid = false;
                    result.message = 'Invalid characters. Windows paths cannot contain: < > : " | ? *';
                }
                break;
                
            case 'macos':
            case 'linux':
                result.isValid = /^[~./]|^\//.test(trimmedPath);
                result.message = result.isValid ? `${os} path looks good!` : 
                    `${os} paths should start with /, ~, or ./`;
                break;
                
            case 'android':
                result.isValid = /^(\/storage\/|\/sdcard\/|\/|~)/.test(trimmedPath);
                result.message = result.isValid ? 'Android path looks good!' : 
                    'Android paths should start with /storage/, /sdcard/, /, or ~';
                break;
                
            case 'ios':
                result.isValid = /^(\/var\/|\/private\/var\/|\/|~)/.test(trimmedPath);
                result.message = result.isValid ? 'iOS path looks good!' : 
                    'iOS paths should start with /var/, /private/var/, /, or ~';
                break;
                
            case 'chromeos':
                result.isValid = /^(\/home\/chronos\/|\/mnt\/|\/|~)/.test(trimmedPath);
                result.message = result.isValid ? 'ChromeOS path looks good!' : 
                    'ChromeOS paths should start with /home/chronos/, /mnt/, /, or ~';
                break;
                
            default:
                result.isValid = trimmedPath.length > 0;
                result.message = 'Path validation not available for this OS';
        }
        
        // Common validation for all OS
        if (result.isValid) {
            if (trimmedPath.endsWith(' ') || trimmedPath.startsWith(' ')) {
                result.isValid = false;
                result.message = 'Path should not start or end with spaces';
            } else if (/([^:]\/\/|^\/\/)/.test(trimmedPath)) {
                result.isValid = false;
                result.message = 'Use single slashes between directories';
            }
        }
        
        return result;
    }

// Initialize event listeners
    initEventListeners() {
        // Event listeners for the application
        // Add any new event listeners here
    }
    
    // Initialize the application
    init() {
        this.detectDevice();
        this.initEventListeners();
        // Other initialization code
    }
    
    detectDevice() {
        const userAgent = navigator.userAgent.toLowerCase();
        const platform = navigator.platform.toLowerCase();
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        let deviceType = 'desktop';
        let os = 'unknown';
        let icon = '🖥️';
        
        // First, detect OS based on user agent and platform
        // Check mobile OS first to avoid conflicts (Android contains "linux", iOS contains "Mac OS X")
        if (/android/.test(userAgent) || /droid/.test(userAgent)) {
            os = 'android';
        } else if (/iphone|ipad|ipod|ios/.test(userAgent)) {
            os = 'ios';
        } else if (/chrome os|cros/.test(userAgent)) {
            os = 'chromeos';
        } else if (/windows|win32|win64|wow32|wow64|windows phone/.test(userAgent) || /win/.test(platform)) {
            os = 'windows';
        } else if (/macintosh|mac os x|macos/.test(userAgent) || /mac/.test(platform)) {
            os = 'macos';
        } else if (/linux|x11/.test(userAgent) || /linux/.test(platform)) {
            os = 'linux';
        }
        
        // Then determine device type
        if (/android.*mobile|iphone|ipod|windows phone/.test(userAgent) || (/android/.test(userAgent) && /mobile/.test(userAgent))) {
            deviceType = 'mobile';
            icon = '📱';
        } else if (/ipad/.test(userAgent) || (/android/.test(userAgent) && !/mobile/.test(userAgent))) {
            deviceType = 'tablet';
            icon = '📱';
        } else if (isTouchDevice && window.innerWidth > 768 && window.innerWidth < 1200) {
            // Touch device with tablet-like dimensions
            deviceType = 'tablet';
            icon = '📱';
            // OS already detected above, don't override
        } else {
            deviceType = 'desktop';
            icon = '🖥️';
        }
        
        // Final fallback for unknown OS
        if (os === 'unknown') {
            // Try to detect based on common patterns, prioritizing mobile OS
            if (/android/.test(userAgent)) {
                os = 'android';
            } else if (/iphone|ipad|ipod|ios/.test(userAgent)) {
                os = 'ios';
            } else if (/chrome os|cros/.test(userAgent)) {
                os = 'chromeos';
            } else if (/windows/.test(userAgent) || /win/.test(platform)) {
                os = 'windows';
            } else if (/mac/.test(userAgent) || /mac/.test(platform)) {
                os = 'macos';
            } else if (/linux/.test(userAgent) || /x11/.test(platform)) {
                os = 'linux';
            } else {
                // Last resort - assume desktop based on screen size
                os = window.innerWidth > 1024 ? 'windows' : 'unknown';
            }
        }
        
        return {
            type: deviceType,
            os: os,
            icon: icon,
            isTouchDevice: isTouchDevice,
            screenWidth: window.innerWidth,
            screenHeight: window.innerHeight,
            userAgent: userAgent,
            platform: platform
        };
    }

    setupDeviceDetection() {
        // Update device info displays
        const updateDeviceInfo = (prefix = '') => {
            const deviceIcon = document.getElementById(`${prefix}device-icon`);
            const deviceText = document.getElementById(`${prefix}device-text`);
            const detectedPlatform = document.getElementById(`${prefix}detected-platform`);
            const platformHelp = document.getElementById(`${prefix}platform-specific-help`);
            
            if (deviceIcon) deviceIcon.textContent = this.deviceInfo.icon;
            
            let deviceDescription = '';
            switch (this.deviceInfo.os) {
                case 'android':
                    deviceDescription = 'Android device detected';
                    break;
                case 'ios':
                    deviceDescription = 'iOS device detected';
                    break;
                case 'windows':
                    deviceDescription = 'Windows computer detected';
                    break;
                case 'macos':
                    deviceDescription = 'Mac computer detected';
                    break;
                case 'linux':
                    deviceDescription = 'Linux computer detected';
                    break;
                case 'chromeos':
                    deviceDescription = 'Chrome OS device detected';
                    break;
                default:
                    deviceDescription = `${this.deviceInfo.type} detected (${this.deviceInfo.os})`;
            }
            
            if (deviceText) deviceText.textContent = deviceDescription;
            if (detectedPlatform) detectedPlatform.textContent = this.deviceInfo.os;
            
            // Update platform-specific help text
            if (platformHelp) {
                let helpText = '';
                switch (this.deviceInfo.os) {
                    case 'android':
                        helpText = 'On Android, common folders are in /storage/emulated/0/ (Downloads, Documents, etc.)';
                        break;
                    case 'ios':
                        helpText = 'On iOS, app documents are typically in sandboxed directories. Use the Files app to find paths.';
                        break;
                    case 'windows':
                        helpText = 'On Windows, use paths like C:\\Users\\YourName\\Documents\\Output';
                        break;
                    case 'macos':
                        helpText = 'On Mac, use paths like /Users/YourName/Documents/Output';
                        break;
                    case 'linux':
                        helpText = 'On Linux, use paths like /home/username/Documents/Output';
                        break;
                    case 'chromeos':
                        helpText = 'On Chrome OS, use paths like /home/chronos/user/Downloads or /home/chronos/user/MyFiles';
                        break;
                    default:
                        helpText = 'Enter the full path to the folder where protected files will be saved.';
                }
                platformHelp.textContent = helpText;
            }
        };
        
        updateDeviceInfo('');
        updateDeviceInfo('batch-');
    }

    setupSmartSuggestions() {
        const createSuggestions = (prefix = '') => {
            const suggestionsContainer = document.getElementById(`${prefix}suggestion-buttons`);
            if (!suggestionsContainer) return;
            
            let suggestions = [];
            
            switch (this.deviceInfo.os) {
                case 'android':
                    suggestions = [
                        { path: '/storage/emulated/0/Download', label: '📥 Downloads', desc: 'Default download folder' },
                        { path: '/storage/emulated/0/Documents', label: '📄 Documents', desc: 'Documents folder' },
                        { path: '/storage/emulated/0/DCIM', label: '📸 Camera', desc: 'Camera photos' },
                        { path: '/sdcard/Download', label: '💾 SD Downloads', desc: 'SD card downloads' }
                    ];
                    break;
                case 'ios':
                    suggestions = [
                        { path: '/var/mobile/Containers/Data/Documents', label: '📄 Documents', desc: 'App documents' },
                        { path: '/var/mobile/Media/DCIM', label: '📸 Photos', desc: 'Photo library' }
                    ];
                    break;
                case 'windows':
                    const username = '%USERNAME%';
                    suggestions = [
                        { path: `C:\\Users\\${username}\\Documents\\DocSeal`, label: '📄 Documents', desc: 'Your documents folder' },
                        { path: `C:\\Users\\${username}\\Desktop\\DocSeal`, label: '🖥️ Desktop', desc: 'Desktop folder' },
                        { path: `C:\\Users\\${username}\\Downloads\\DocSeal`, label: '📥 Downloads', desc: 'Downloads folder' },
                        { path: 'C:\\DocSeal', label: '💾 C: Drive', desc: 'Root of C: drive' }
                    ];
                    break;
                case 'macos':
                    suggestions = [
                        { path: '/Users/$USER/Documents/DocSeal', label: '📄 Documents', desc: 'Your documents folder' },
                        { path: '/Users/$USER/Desktop/DocSeal', label: '🖥️ Desktop', desc: 'Desktop folder' },
                        { path: '/Users/$USER/Downloads/DocSeal', label: '📥 Downloads', desc: 'Downloads folder' },
                        { path: '/tmp/DocSeal', label: '⚡ Temporary', desc: 'Temporary folder' }
                    ];
                    break;
                case 'linux':
                    suggestions = [
                        { path: '/home/$USER/Documents/DocSeal', label: '📄 Documents', desc: 'Your documents folder' },
                        { path: '/home/$USER/Desktop/DocSeal', label: '🖥️ Desktop', desc: 'Desktop folder' },
                        { path: '/home/$USER/Downloads/DocSeal', label: '📥 Downloads', desc: 'Downloads folder' },
                        { path: '/tmp/DocSeal', label: '⚡ Temporary', desc: 'Temporary folder' }
                    ];
                    break;
                case 'chromeos':
                    suggestions = [
                        { path: '/home/chronos/user/MyFiles/Documents/DocSeal', label: '📄 Documents', desc: 'Your documents folder' },
                        { path: '/home/chronos/user/Downloads/DocSeal', label: '📥 Downloads', desc: 'Downloads folder' },
                        { path: '/home/chronos/user/MyFiles/DocSeal', label: '📁 My Files', desc: 'My Files folder' }
                    ];
                    break;
                default:
                    suggestions = [
                        { path: '/Documents/DocSeal', label: '📄 Documents', desc: 'Documents folder' },
                        { path: '/Downloads/DocSeal', label: '📥 Downloads', desc: 'Downloads folder' }
                    ];
            }
            
            suggestionsContainer.innerHTML = '';
            
            suggestions.forEach(suggestion => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'suggestion-btn';
                button.innerHTML = `
                    <span class="icon">${suggestion.label.split(' ')[0]}</span>
                    <span>${suggestion.label.split(' ').slice(1).join(' ')}</span>
                `;
                button.title = suggestion.desc;
                
                button.addEventListener('click', () => {
                    const input = document.getElementById(`${prefix}output-folder`);
                    if (input) {
                        input.value = suggestion.path;
                        input.dispatchEvent(new Event('input'));
                        this.updateStatus(`Selected: ${suggestion.label}`);
                    }
                });
                
                suggestionsContainer.appendChild(button);
            });
        };
        
        createSuggestions('');
        createSuggestions('batch-');
    }

    updateFolderStatus(inputId, isValid, message) {
        const prefix = inputId.includes('batch') ? 'batch-' : '';
        const statusContainer = document.getElementById(`${prefix}folder-status`);
        const statusText = document.getElementById(`${prefix}status-text`);
        
        if (!statusContainer || !statusText) return;
        
        // Remove existing status classes
        statusContainer.classList.remove('valid', 'invalid', 'neutral');
        
        // Add appropriate class and update text
        if (isValid === null) {
            statusContainer.classList.add('neutral');
            statusText.textContent = message || 'Enter a folder path above';
        } else if (isValid) {
            statusContainer.classList.add('valid');
            statusText.textContent = message || 'Folder path looks good!';
        } else {
            statusContainer.classList.add('invalid');
            statusText.textContent = message || 'Please check the folder path';
        }
    }

    showFolderHelpDialog() {
        const deviceSpecificHelp = this.getDeviceSpecificHelp();
        
        const helpText = `
            <div style="padding: 20px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <span style="font-size: 1.5rem;">${this.deviceInfo.icon}</span>
                    <h3 style="margin: 0; color: #333;">Folder Setup for ${this.deviceInfo.os.charAt(0).toUpperCase() + this.deviceInfo.os.slice(1)}</h3>
                </div>
                
                <p style="margin-bottom: 15px; color: #666; line-height: 1.6;">
                    ${deviceSpecificHelp.description}
                </p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="margin-bottom: 10px; color: #333;">📁 Recommended Paths:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666; line-height: 1.8;">
                        ${deviceSpecificHelp.examples.map(example => `<li><strong>${example.label}:</strong> <code style="background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-family: monospace;">${example.path}</code></li>`).join('')}
                    </ul>
                </div>
                
                ${deviceSpecificHelp.tips ? `
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3;">
                    <h4 style="margin-bottom: 8px; color: #1976d2;">💡 Tips:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #1565c0; line-height: 1.6;">
                        ${deviceSpecificHelp.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <p style="margin-top: 15px; color: #666; font-size: 0.9em;">
                    <strong>Note:</strong> The folder must exist and be accessible by your browser/device.
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
            padding: 20px;
            box-sizing: border-box;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 12px;
            max-width: 600px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
        `;
        
        modalContent.innerHTML = helpText;
        
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Got it!';
        closeButton.style.cssText = `
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            margin: 20px;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.2s ease;
        `;
        closeButton.onmouseover = () => closeButton.style.background = '#5a67d8';
        closeButton.onmouseout = () => closeButton.style.background = '#667eea';
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
        
        // Close on escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    getDeviceSpecificHelp() {
        switch (this.deviceInfo.os) {
            case 'android':
                return {
                    description: 'On Android devices, you can access various storage locations. The most common paths start with /storage/emulated/0/ which represents your internal storage.',
                    examples: [
                        { label: 'Downloads', path: '/storage/emulated/0/Download' },
                        { label: 'Documents', path: '/storage/emulated/0/Documents' },
                        { label: 'Pictures', path: '/storage/emulated/0/Pictures' },
                        { label: 'SD Card', path: '/sdcard/Download' }
                    ],
                    tips: [
                        'Use a file manager app to navigate and find the exact path',
                        'Create a "DocSeal" folder in Downloads for easy access',
                        'Some apps may have restricted access to certain folders'
                    ]
                };
            case 'ios':
                return {
                    description: 'iOS uses a sandboxed file system. Apps can only access specific directories. Use the Files app to navigate and find accessible folders.',
                    examples: [
                        { label: 'iCloud Drive', path: '/var/mobile/Library/Mobile Documents' },
                        { label: 'App Documents', path: '/var/mobile/Containers/Data/Documents' }
                    ],
                    tips: [
                        'Use the Files app to create and navigate folders',
                        'iCloud Drive folders are often the most accessible',
                        'Some paths may vary depending on iOS version'
                    ]
                };
            case 'windows':
                return {
                    description: 'Windows uses drive letters (C:, D:, etc.) and backslashes for folder paths. Replace %USERNAME% with your actual username.',
                    examples: [
                        { label: 'Documents', path: 'C:\\Users\\%USERNAME%\\Documents\\DocSeal' },
                        { label: 'Desktop', path: 'C:\\Users\\%USERNAME%\\Desktop\\DocSeal' },
                        { label: 'Downloads', path: 'C:\\Users\\%USERNAME%\\Downloads\\DocSeal' }
                    ],
                    tips: [
                        'Use File Explorer to copy the exact path',
                        'Right-click a folder and select "Properties" to see the full path',
                        'Create a dedicated "DocSeal" folder for organization'
                    ]
                };
            case 'macos':
                return {
                    description: 'macOS uses forward slashes for folder paths. Replace $USER with your actual username.',
                    examples: [
                        { label: 'Documents', path: '/Users/$USER/Documents/DocSeal' },
                        { label: 'Desktop', path: '/Users/$USER/Desktop/DocSeal' },
                        { label: 'Downloads', path: '/Users/$USER/Downloads/DocSeal' }
                    ],
                    tips: [
                        'Use Finder to navigate and copy folder paths',
                        'Right-click a folder and hold Option to see "Copy as Pathname"',
                        'The ~ symbol represents your home directory (/Users/$USER)'
                    ]
                };
            case 'linux':
                return {
                    description: 'Linux uses forward slashes for folder paths. Replace $USER with your actual username.',
                    examples: [
                        { label: 'Documents', path: '/home/$USER/Documents/DocSeal' },
                        { label: 'Desktop', path: '/home/$USER/Desktop/DocSeal' },
                        { label: 'Downloads', path: '/home/$USER/Downloads/DocSeal' }
                    ],
                    tips: [
                        'Use the file manager or terminal to navigate folders',
                        'The ~ symbol represents your home directory (/home/$USER)',
                        'Use "pwd" command in terminal to see current directory path'
                    ]
                };
            case 'chromeos':
                return {
                    description: 'Chrome OS uses Linux-style paths. Files are typically stored in the chronos user directory.',
                    examples: [
                        { label: 'Downloads', path: '/home/chronos/user/Downloads/DocSeal' },
                        { label: 'My Files', path: '/home/chronos/user/MyFiles/DocSeal' },
                        { label: 'Documents', path: '/home/chronos/user/MyFiles/Documents/DocSeal' }
                    ],
                    tips: [
                        'Use the Files app to navigate and create folders',
                        'Downloads folder is easily accessible',
                        'My Files contains your personal documents and folders'
                    ]
                };
            default:
                return {
                    description: 'Enter the full path to the folder where you want to save protected files.',
                    examples: [
                        { label: 'Documents', path: '/Documents/DocSeal' },
                        { label: 'Downloads', path: '/Downloads/DocSeal' }
                    ]
                };
        }
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