// DOM Elements - with null checks
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const jobSuggestionsList = document.getElementById('jobSuggestionsList');

// Store current analysis data
let currentAnalysisData = null;

// Job Suggestion Elements
const jobResumeInput = document.getElementById('jobResumeInput');
const jobUploadArea = document.getElementById('jobUploadArea');
const jobUploadContainer = document.getElementById('jobUploadContainer');
const jobLoading = document.getElementById('jobLoading');
const jobSuggestionsResults = document.getElementById('jobSuggestionsResults');
const jobSuggestionsGrid = document.getElementById('jobSuggestionsGrid');
const jobMatchSummary = document.getElementById('jobMatchSummary');

// File input change handler - with null check
if (fileInput && fileName && fileInfo) {
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            fileInfo.style.display = 'flex';
        } else {
            fileInfo.style.display = 'none';
        }
    });
}

// Form submission handler - with null check
if (uploadForm && uploadSection && loadingSection && resultsSection) {
    uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    // Show loading, hide upload and results
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'block';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        const data = await response.json();
        currentAnalysisData = data; // Store analysis data for download
        displayResults(data);
        
    } catch (error) {
        alert('Error: ' + error.message);
        resetToUpload();
    }
    });
}

// Display analysis results
function displayResults(data) {
    // Hide loading, show results - with null checks
    if (loadingSection) loadingSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'block';
    
    // Update ATS Score
    updateATSScore(data.ats_score);
    
    // Update Contact Information
    updateContactInfo(data.contact_info);
    
    // Update Skills
    updateSkills(data.skills);
    
    // Update Experience
    updateExperience(data.years_experience, data.mentioned_titles);
    
    // Update Education
    updateEducation(data.sections);
    
    // Update Sections
    updateSections(data.sections);
    
    // Update Statistics
    updateStatistics(data);
    
    // Update Suggestions
    updateSuggestions(data.suggestions);
    
    // Update Job Suggestions
    updateJobSuggestions(data.job_suggestions);
}

// Update ATS Score
function updateATSScore(score) {
    const scoreElement = document.getElementById('atsScore');
    const scoreProgress = document.getElementById('scoreProgress');
    const scoreDescription = document.getElementById('scoreDescription');
    
    if (!scoreElement || !scoreProgress || !scoreDescription) return; // Safety check
    
    scoreElement.textContent = score;
    
    // Calculate stroke-dashoffset (565.48 is circumference for r=90)
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (score / 100) * circumference;
    scoreProgress.style.strokeDashoffset = offset;
    
    // Update color based on score
    if (score >= 80) {
        scoreProgress.style.stroke = '#10b981';
        scoreDescription.textContent = 'Excellent! Your resume is highly ATS-compatible.';
    } else if (score >= 60) {
        scoreProgress.style.stroke = '#3b82f6';
        scoreDescription.textContent = 'Good! Your resume is mostly ATS-compatible with room for improvement.';
    } else if (score >= 40) {
        scoreProgress.style.stroke = '#f59e0b';
        scoreDescription.textContent = 'Fair. Consider implementing the suggestions below to improve your ATS score.';
    } else {
        scoreProgress.style.stroke = '#ef4444';
        scoreDescription.textContent = 'Needs improvement. Follow the suggestions to enhance your resume.';
    }
}

// Update Contact Information
function updateContactInfo(contactInfo) {
    const contactDiv = document.getElementById('contactInfo');
    if (!contactDiv) return; // Safety check
    
    let html = '';
    
    if (contactInfo && contactInfo.emails && contactInfo.emails.length > 0) {
        contactInfo.emails.forEach(email => {
            html += `
                <div class="contact-item">
                    <i class="fas fa-envelope"></i>
                    <span>${email}</span>
                </div>
            `;
        });
    } else {
        html += '<p style="color: var(--error-color);">No email found</p>';
    }
    
    if (contactInfo && contactInfo.phones && contactInfo.phones.length > 0) {
        contactInfo.phones.forEach(phone => {
            html += `
                <div class="contact-item">
                    <i class="fas fa-phone"></i>
                    <span>${phone}</span>
                </div>
            `;
        });
    } else {
        html += '<p style="color: var(--warning-color);">No phone number found</p>';
    }
    
    contactDiv.innerHTML = html;
}

// Update Skills
function updateSkills(skills) {
    const skillsList = document.getElementById('skillsList');
    if (!skillsList) return; // Safety check
    
    if (skills && skills.length > 0) {
        skillsList.innerHTML = skills.map(skill => 
            `<span class="skill-tag">${skill}</span>`
        ).join('');
    } else {
        skillsList.innerHTML = '<p style="color: var(--text-secondary);">No skills detected</p>';
    }
}

// Update Experience
function updateExperience(years, titles) {
    const experienceDiv = document.getElementById('experienceInfo');
    if (!experienceDiv) return; // Safety check
    
    let html = '';
    
    if (years > 0) {
        html += `<p><strong>Years of Experience:</strong> ${years} years</p>`;
    } else {
        html += '<p style="color: var(--warning-color);">Experience information not clearly stated</p>';
    }
    
    if (titles && titles.length > 0) {
        html += `<p style="margin-top: 10px;"><strong>Mentioned Roles:</strong> ${titles.join(', ')}</p>`;
    }
    
    experienceDiv.innerHTML = html;
}

// Update Education
function updateEducation(sections) {
    const educationDiv = document.getElementById('educationInfo');
    if (!educationDiv) return; // Safety check
    
    let html = '';
    
    if (sections && sections.education) {
        html += `<p>${sections.education.substring(0, 200)}${sections.education.length > 200 ? '...' : ''}</p>`;
    } else {
        html += '<p style="color: var(--text-secondary);">No education section detected</p>';
    }
    
    educationDiv.innerHTML = html;
}

// Update Statistics
function updateStatistics(data) {
    const statsDiv = document.getElementById('statisticsInfo');
    if (!statsDiv) return; // Safety check
    
    const html = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
            <div>
                <strong>Word Count:</strong><br>
                <span style="color: var(--primary-color); font-size: 1.2rem; font-weight: 600;">${data.word_count || 0}</span>
            </div>
            <div>
                <strong>Character Count:</strong><br>
                <span style="color: var(--primary-color); font-size: 1.2rem; font-weight: 600;">${data.character_count || 0}</span>
            </div>
            <div>
                <strong>Skills Found:</strong><br>
                <span style="color: var(--primary-color); font-size: 1.2rem; font-weight: 600;">${data.skills?.length || 0}</span>
            </div>
            <div>
                <strong>Analysis Date:</strong><br>
                <span style="color: var(--text-secondary); font-size: 0.9rem;">${data.analysis_date || 'N/A'}</span>
            </div>
        </div>
    `;
    statsDiv.innerHTML = html;
}

// Update Suggestions
function updateSuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestionsList');
    if (!suggestionsList) return; // Safety check
    
    if (!suggestions || suggestions.length === 0) {
        suggestionsList.innerHTML = '<p style="color: var(--success-color);">Great job! No major issues found.</p>';
        return;
    }
    
    const iconMap = {
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    suggestionsList.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item ${suggestion.type}">
            <i class="${iconMap[suggestion.type] || 'fas fa-info-circle'} suggestion-icon"></i>
            <div class="suggestion-content">
                <h4>${suggestion.title || 'Suggestion'}</h4>
                <p>${suggestion.message || ''}</p>
            </div>
        </div>
    `).join('');
}

// Update Sections
function updateSections(sections) {
    // Try both possible element IDs
    const sectionsInfo = document.getElementById('sectionsInfo');
    const sectionsGrid = document.getElementById('sectionsGrid');
    const targetElement = sectionsInfo || sectionsGrid;
    
    if (!targetElement) return; // Safety check
    
    if (!sections || Object.keys(sections).length === 0) {
        targetElement.innerHTML = '<p style="color: var(--text-secondary);">No sections detected in resume.</p>';
        return;
    }
    
    const sectionTitles = {
        'summary': 'Summary/Objective',
        'experience': 'Experience',
        'education': 'Education',
        'skills': 'Skills'
    };
    
    let html = '';
    Object.entries(sections).forEach(([key, value]) => {
        const title = sectionTitles[key] || key.charAt(0).toUpperCase() + key.slice(1);
        const content = value && value !== 'Not found' 
            ? (value.length > 200 ? value.substring(0, 200) + '...' : value) 
            : 'Section not found or could not be extracted';
        html += `
            <div style="margin-bottom: 15px; padding: 10px; background: var(--bg-color, #f8f9fa); border-radius: 8px;">
                <h4 style="margin-bottom: 8px; color: var(--primary-color, #667eea);">${title}</h4>
                <p style="color: var(--text-color, #333); line-height: 1.6;">${content}</p>
            </div>
        `;
    });
    
    targetElement.innerHTML = html;
}

// Update Job Suggestions
function updateJobSuggestions(suggestions) {
    if (!jobSuggestionsList) return;
    
    if (!suggestions || suggestions.length === 0) {
        jobSuggestionsList.innerHTML = '<p style="color: var(--text-secondary);">Upload a resume to unlock curated job suggestions.</p>';
        return;
    }
    
    jobSuggestionsList.innerHTML = suggestions.map(job => `
        <div class="job-card">
            <span class="match-score">Match Score: ${job.match_score}%</span>
            <h3>${job.title}</h3>
            <p>${job.description}</p>
            <ul>
                ${job.companies.map(company => `<li>${company}</li>`).join('')}
            </ul>
        </div>
    `).join('');
}

// Reset to upload state
function resetToUpload() {
    if (uploadSection) uploadSection.style.display = 'block';
    if (loadingSection) loadingSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
}

// Reset analysis (called from button)
function resetAnalysis() {
    resetToUpload();
    currentAnalysisData = null; // Clear stored data
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Download report function
async function downloadReport() {
    if (!currentAnalysisData) {
        alert('No analysis data available. Please analyze a resume first.');
        return;
    }
    
    try {
        const downloadBtn = document.getElementById('downloadBtn');
        if (!downloadBtn) {
            alert('Download button not found');
            return;
        }
        const originalText = downloadBtn.innerHTML;
        
        // Show loading state
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Report...';
        
        // Send request to download endpoint
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentAnalysisData)
        });
        
        if (!response.ok) {
            // Check if response is JSON before parsing
            const contentType = response.headers.get('content-type');
            let errorMessage = 'Download failed';
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    const error = await response.json();
                    errorMessage = error.error || error.message || 'Download failed';
                } catch (e) {
                    errorMessage = `Server error (${response.status})`;
                }
            } else {
                // If not JSON, try to get text or use status
                try {
                    const text = await response.text();
                    errorMessage = text || `Server error (${response.status})`;
                } catch (e) {
                    errorMessage = `Server error (${response.status})`;
                }
            }
            
            throw new Error(errorMessage);
        }
        
        // Get the blob and create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Get filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'resume_analysis_report.pdf';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Reset button
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = originalText;
        
    } catch (error) {
        alert('Error downloading report: ' + error.message);
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Download PDF Report';
    }
}

// Resume Builder Functions
function openResumeBuilder(templateId) {
    const modal = document.getElementById('resumeBuilderModal');
    const selectedTemplate = document.getElementById('selectedTemplate');
    
    console.log('Opening resume builder with template:', templateId);
    
    if (selectedTemplate) {
        selectedTemplate.value = templateId;
        console.log('Template ID set to:', selectedTemplate.value);
    } else {
        console.error('selectedTemplate element not found!');
    }
    
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        modal.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        console.error('resumeBuilderModal element not found!');
    }
}

function closeResumeBuilder() {
    const modal = document.getElementById('resumeBuilderModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        document.getElementById('resumeForm').reset();
        // Clear certificate preview
        const certificatesPreview = document.getElementById('certificatesPreview');
        if (certificatesPreview) {
            certificatesPreview.innerHTML = '';
        }
    }
}

// Job Suggestion Upload Handler
if (jobResumeInput) {
    jobResumeInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Validate file
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|txt)$/i)) {
            alert('Please upload a PDF, DOCX, or TXT file');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }
        
        // Show loading, hide upload and results
        jobUploadContainer.style.display = 'none';
        jobSuggestionsResults.style.display = 'none';
        jobLoading.style.display = 'block';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/job-suggestions', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to analyze resume');
            }
            
            const data = await response.json();
            
            // Hide loading, show results
            jobLoading.style.display = 'none';
            jobSuggestionsResults.style.display = 'block';
            
            // Display job suggestions
            displayJobSuggestions(data.job_suggestions, data.analysis_summary);
            
        } catch (error) {
            jobLoading.style.display = 'none';
            jobUploadContainer.style.display = 'block';
            alert('Error: ' + error.message);
        }
    });
}

// Drag and drop for job upload
if (jobUploadArea) {
    jobUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        jobUploadArea.style.borderColor = 'var(--primary-color)';
        jobUploadArea.style.backgroundColor = 'rgba(99, 102, 241, 0.1)';
    });
    
    jobUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        jobUploadArea.style.borderColor = 'var(--border-color)';
        jobUploadArea.style.backgroundColor = 'transparent';
    });
    
    jobUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        jobUploadArea.style.borderColor = 'var(--border-color)';
        jobUploadArea.style.backgroundColor = 'transparent';
        
        const file = e.dataTransfer.files[0];
        if (file) {
            jobResumeInput.files = e.dataTransfer.files;
            jobResumeInput.dispatchEvent(new Event('change'));
        }
    });
}

function displayJobSuggestions(jobs, summary) {
    if (!jobs || jobs.length === 0) {
        jobSuggestionsGrid.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 40px;">No job matches found. Try adding more skills and experience to your resume.</p>';
        return;
    }
    
    // Update summary
    if (jobMatchSummary) {
        jobMatchSummary.textContent = `Found ${jobs.length} job matches based on ${summary.skills_count} skills and ${summary.experience_years || 0} years of experience`;
    }
    
    // Clear and populate grid
    jobSuggestionsGrid.innerHTML = '';
    
    jobs.forEach((job, index) => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-suggestion-card';
        
        // Category color mapping
        const categoryColors = {
            'Engineering': 'var(--primary-color)',
            'AI/ML': '#8B5CF6',
            'Web Development': '#10B981',
            'Data Science': '#3B82F6',
            'Infrastructure': '#F59E0B',
            'Mobile': '#EC4899',
            'Security': '#EF4444',
            'Data Engineering': '#06B6D4',
            'General': '#6B7280'
        };
        
        const categoryColor = categoryColors[job.category] || 'var(--primary-color)';
        
        // Companies list
        const companiesList = job.companies.slice(0, 3).join(', ');
        
        jobCard.innerHTML = `
            <div class="job-card-header">
                <span class="job-category" style="background: ${categoryColor}20; color: ${categoryColor};">
                    ${job.category}
                </span>
                <div class="job-match-score">
                    <span class="match-percentage">${job.match_score}%</span>
                    <span class="match-label">Match</span>
                </div>
            </div>
            <h3 class="job-title">${job.title}</h3>
            <p class="job-description">${job.description}</p>
            <div class="job-details">
                <div class="job-detail-item">
                    <i class="fas fa-building"></i>
                    <span>${companiesList}${job.companies.length > 3 ? ' +' + (job.companies.length - 3) + ' more' : ''}</span>
                </div>
                <div class="job-detail-item">
                    <i class="fas fa-dollar-sign"></i>
                    <span>${job.salary_range}</span>
                </div>
                <div class="job-detail-item">
                    <i class="fas fa-laptop"></i>
                    <span>${job.remote ? 'Remote Available' : 'On-site'}</span>
                </div>
            </div>
            <div class="job-card-footer">
                <button class="btn-apply" onclick="window.open('https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(job.title)}', '_blank')">
                    <i class="fas fa-external-link-alt"></i> View Similar Jobs
                </button>
            </div>
        `;
        
        jobSuggestionsGrid.appendChild(jobCard);
    });
}

// Reset job suggestions
function resetJobSuggestions() {
    if (jobResumeInput) jobResumeInput.value = '';
    if (jobUploadContainer) jobUploadContainer.style.display = 'block';
    if (jobLoading) jobLoading.style.display = 'none';
    if (jobSuggestionsResults) jobSuggestionsResults.style.display = 'none';
}

// Certificate file preview
const certificatesInput = document.getElementById('certificatesInput');
const certificatesPreview = document.getElementById('certificatesPreview');

if (certificatesInput && certificatesPreview) {
    certificatesInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        certificatesPreview.innerHTML = '';
        
        if (files.length === 0) {
            return;
        }
        
        // Limit to 5 files
        if (files.length > 5) {
            alert('Maximum 5 certificate files allowed. Only the first 5 will be uploaded.');
            e.target.value = '';
            return;
        }
        
        // Check file sizes (5MB each)
        const maxSize = 5 * 1024 * 1024; // 5MB
        const oversizedFiles = files.filter(file => file.size > maxSize);
        
        if (oversizedFiles.length > 0) {
            alert(`Some files exceed 5MB limit: ${oversizedFiles.map(f => f.name).join(', ')}`);
            e.target.value = '';
            certificatesPreview.innerHTML = '';
            return;
        }
        
        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.style.cssText = 'display: flex; align-items: center; gap: 10px; padding: 10px; background: var(--bg-color); border-radius: 8px; border: 1px solid var(--border-color);';
            
            // Determine icon based on file type
            let iconClass = 'fas fa-file';
            if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
                iconClass = 'fas fa-file-pdf';
            } else if (file.type.startsWith('image/')) {
                iconClass = 'fas fa-file-image';
            }
            
            fileItem.innerHTML = `
                <i class="${iconClass}" style="color: var(--primary-color); font-size: 1.2rem;"></i>
                <span style="flex: 1; font-size: 0.9rem; color: var(--text-primary);">${file.name}</span>
                <span style="color: var(--text-secondary); font-size: 0.85rem;">${(file.size / 1024 / 1024).toFixed(2)} MB</span>
            `;
            certificatesPreview.appendChild(fileItem);
        });
    });
}

// Resume Form Submission
const resumeForm = document.getElementById('resumeForm');
if (resumeForm) {
    resumeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(resumeForm);
        const templateId = formData.get('template_id');
        
        console.log('Form submitted. Template ID:', templateId);
        console.log('Form data:', Object.fromEntries(formData.entries()));
        
        if (!templateId) {
            alert('Please select a template first');
            console.error('Template ID is missing!');
            return;
        }
        
        // Validate required fields
        if (!formData.get('full_name') || !formData.get('email')) {
            alert('Full Name and Email are required fields.');
            return;
        }
        
        // Validate experience and education are not empty
        if (!formData.get('experience') || !formData.get('experience').trim()) {
            alert('Professional Experience is required.');
            return;
        }
        
        if (!formData.get('education') || !formData.get('education').trim()) {
            alert('Education is required.');
            return;
        }
        
        const submitBtn = resumeForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Resume...';
        
        try {
            console.log('Sending request to /api/templates/generate...');
            console.log('FormData entries:', Array.from(formData.entries()).map(([k, v]) => [k, typeof v === 'string' ? v.substring(0, 50) : v.name || 'File']));
            
            // Send FormData directly (includes files)
            const response = await fetch('/api/templates/generate', {
                method: 'POST',
                body: formData  // Don't set Content-Type header, browser will set it with boundary
            });
            
            console.log('Response received:', {
                status: response.status,
                statusText: response.statusText,
                contentType: response.headers.get('content-type'),
                ok: response.ok
            });
            
            // Check response status and content type first
            const contentType = response.headers.get('content-type');
            console.log('Response Status:', response.status);
            console.log('Response OK:', response.ok);
            console.log('Response Content-Type:', contentType);
            
            if (!response.ok) {
                // Response is not OK, try to get error message
                const errorText = await response.text();
                console.error('Error response:', errorText);
                try {
                    const error = JSON.parse(errorText);
                    throw new Error(error.error || 'Resume generation failed');
                } catch {
                    throw new Error(errorText || `Server error: ${response.status}`);
                }
            }
            
            // Check if response is PDF
            if (!contentType || !contentType.includes('application/pdf')) {
                // If not PDF, it might be an error - clone response to read it
                const clonedResponse = response.clone();
                const errorText = await clonedResponse.text();
                console.error('Non-PDF response:', errorText);
                try {
                    const error = JSON.parse(errorText);
                    throw new Error(error.error || 'Resume generation failed');
                } catch {
                    throw new Error(errorText || 'Unexpected response format. Expected PDF but got: ' + contentType);
                }
            }
            
            // Download the PDF - simplified and more reliable approach
            const blob = await response.blob();
            console.log('✓ PDF Blob received - size:', blob.size, 'bytes, type:', blob.type);
            
            // Verify blob is not empty
            if (blob.size === 0) {
                throw new Error('Generated PDF is empty. Please check your input data.');
            }
            
            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `resume_${templateId}_${new Date().getTime()}.pdf`;
            if (contentDisposition) {
                // Try multiple patterns to extract filename
                const patterns = [
                    /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/,
                    /filename="?([^"]+)"?/,
                    /filename=([^;]+)/
                ];
                for (const pattern of patterns) {
                    const match = contentDisposition.match(pattern);
                    if (match && match[1]) {
                        filename = match[1].replace(/['"]/g, '').trim();
                        break;
                    }
                }
            }
            
            console.log('✓ Attempting to download PDF with filename:', filename);
            
            // Create and trigger download - simplified and more reliable
            console.log('Creating download link...');
            const url = window.URL.createObjectURL(blob);
            const downloadLink = document.createElement('a');
            downloadLink.href = url;
            downloadLink.download = filename;
            downloadLink.style.display = 'none';
            
            // Add to DOM
            document.body.appendChild(downloadLink);
            console.log('✓ Download link added to DOM');
            
            // Trigger download immediately
            try {
                downloadLink.click();
                console.log('✓ Download click triggered');
                
                // Show success message
                setTimeout(() => {
                    alert('Resume PDF generated successfully! Check your downloads folder.');
                    closeResumeBuilder();
                }, 500);
                
                // Clean up after download
                setTimeout(() => {
                    if (downloadLink.parentNode) {
                        document.body.removeChild(downloadLink);
                    }
                    window.URL.revokeObjectURL(url);
                    console.log('✓ Cleanup completed');
                }, 3000);
            } catch (clickError) {
                console.error('Error triggering download:', clickError);
                // Fallback: try opening in new window
                window.open(url, '_blank');
                alert('Resume PDF generated! It opened in a new tab. Please save it manually.');
                closeResumeBuilder();
            }
            
        } catch (error) {
            console.error('Resume generation error:', error);
            console.error('Error stack:', error.stack);
            
            // Show detailed error message
            let errorMsg = 'Error generating resume: ' + error.message;
            if (error.message.includes('Failed to fetch')) {
                errorMsg += '\n\nPossible causes:\n- Server is not running\n- Network connection issue\n- CORS error';
            }
            
            alert(errorMsg);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('resumeBuilderModal');
    if (e.target === modal) {
        closeResumeBuilder();
    }
});

