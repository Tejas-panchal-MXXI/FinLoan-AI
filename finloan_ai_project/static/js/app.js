/*!
 * FinLoan AI - Complete Custom JavaScript
 * Version: 1.0.0
 * Author: FinLoan AI Team
 * Description: Custom JavaScript for FinLoan AI loan prediction platform
 */

'use strict';

// Global variables
let currentStep = 1;
let formValidation = {
    step1: false,
    step2: false,
    step3: false
};

// Initialize application when DOM is ready
$(document).ready(function() {
    console.log('🚀 FinLoan AI - Application Initialized');
    
    // Initialize all components
    initializeComponents();
    initializeFormValidation();
    initializeEventListeners();
    initializeAnimations();
    
    console.log('✅ All components loaded successfully');
});

/**
 * Initialize all Bootstrap and custom components
 */
function initializeComponents() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize custom dropdowns
    $('.dropdown-toggle').dropdown();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Initialize progress bars
    animateProgressBars();
    
    // Initialize counters
    animateCounters();
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Custom validation rules
    if (typeof $.validator !== 'undefined') {
        // Extend jQuery Validator with custom methods
        $.validator.addMethod("positiveInteger", function(value, element) {
            return this.optional(element) || (parseInt(value) > 0);
        }, "Please enter a positive number");

        $.validator.addMethod("validIncome", function(value, element) {
            return this.optional(element) || (parseInt(value) >= 1000);
        }, "Income must be at least 1000");

        $.validator.addMethod("validLoanAmount", function(value, element) {
            return this.optional(element) || (parseInt(value) >= 10 && parseInt(value) <= 1000);
        }, "Loan amount must be between 10K and 1000K");
    }

    // Real-time validation for form fields
    $('input, select, textarea').on('blur change', function() {
        validateField($(this));
    });

    // Validate on input for better UX
    $('input[type="number"], input[type="text"]').on('input', function() {
        const $field = $(this);
        setTimeout(function() {
            validateField($field);
        }, 500);
    });
}

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 80
            }, 1000, 'easeInOutExpo');
        }
    });

    // Form submission with loading
    $('form').on('submit', function(e) {
        const form = $(this);
        
        if (form.attr('id') === 'loanApplicationForm') {
            if (!validateCompleteForm()) {
                e.preventDefault();
                showAlert('Please fill in all required fields correctly.', 'warning');
                return false;
            }
        }

        // Show loading overlay
        showLoading('Processing your request...');
        
        // Allow form to submit normally
        return true;
    });

    // Multi-step form navigation
    $('.btn-next').on('click', function() {
        const currentStepNum = parseInt($(this).data('step'));
        nextStep(currentStepNum);
    });

    $('.btn-prev').on('click', function() {
        const currentStepNum = parseInt($(this).data('step'));
        prevStep(currentStepNum);
    });

    // Search functionality
    $('#searchInput').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        filterTable(searchTerm);
    });

    // Filter functionality
    $('.filter-select').on('change', function() {
        applyFilters();
    });

    // Export functionality
    $('#exportBtn').on('click', function() {
        exportTableData();
    });

    // Card hover effects
    $('.card').hover(
        function() {
            $(this).addClass('shadow-lg').css('transform', 'translateY(-5px)');
        },
        function() {
            $(this).removeClass('shadow-lg').css('transform', 'translateY(0)');
        }
    );

    // Button click animations
    $('.btn').on('click', function() {
        const button = $(this);
        button.addClass('animate-pulse');
        setTimeout(function() {
            button.removeClass('animate-pulse');
        }, 600);
    });

    // Navbar scroll effect
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });

    // Modal events
    $('.modal').on('show.bs.modal', function() {
        $('body').addClass('modal-open-custom');
    });

    $('.modal').on('hide.bs.modal', function() {
        $('body').removeClass('modal-open-custom');
    });
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Intersection Observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.card, .feature-card, .stats-card').forEach(el => {
            observer.observe(el);
        });
    }

    // Typing animation for hero text
    if ($('.hero-typing').length) {
        typeWriter('.hero-typing', 'Smart Loan Approval & Risk Analysis', 100);
    }
}

/**
 * Multi-step form functions
 */
function showStep(step) {
    $('.form-step').removeClass('active');
    $(`#step-${step}`).addClass('active');
    
    // Update step indicators
    $('.step').removeClass('active completed');
    for (let i = 1; i < step; i++) {
        $(`.step[data-step="${i}"]`).addClass('completed');
    }
    $(`.step[data-step="${step}"]`).addClass('active');
    
    // Update progress bar
    const progress = (step / 3) * 100;
    $('.progress-bar').css('width', progress + '%');
}

function nextStep(current) {
    if (validateStep(current)) {
        currentStep = current + 1;
        showStep(currentStep);
        
        // Scroll to top of form
        $('html, body').animate({
            scrollTop: $('.card-header').offset().top - 100
        }, 500);
    } else {
        showAlert('Please complete all required fields in this step.', 'warning');
    }
}

function prevStep(current) {
    currentStep = current - 1;
    showStep(currentStep);
    
    // Scroll to top of form
    $('html, body').animate({
        scrollTop: $('.card-header').offset().top - 100
    }, 500);
}

function validateStep(step) {
    let isValid = true;
    const stepElement = $(`#step-${step}`);
    
    stepElement.find('input[required], select[required]').each(function() {
        if (!validateField($(this))) {
            isValid = false;
        }
    });
    
    formValidation[`step${step}`] = isValid;
    return isValid;
}

/**
 * Form validation functions
 */
function validateField($field) {
    const value = $field.val();
    const fieldType = $field.attr('type');
    const fieldName = $field.attr('name');
    const isRequired = $field.prop('required');
    
    let isValid = true;
    let errorMessage = '';

    // Check if required field is empty
    if (isRequired && (!value || value.trim() === '')) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Specific validations based on field
    if (value && !isValid === false) {
        switch (fieldName) {
            case 'applicant_income':
                if (parseInt(value) < 1000) {
                    isValid = false;
                    errorMessage = 'Income must be at least 1000';
                }
                break;
                
            case 'loan_amount':
                if (parseInt(value) < 10 || parseInt(value) > 1000) {
                    isValid = false;
                    errorMessage = 'Loan amount must be between 10K and 1000K';
                }
                break;
                
            case 'applicant_name':
                if (value.length < 2) {
                    isValid = false;
                    errorMessage = 'Name must be at least 2 characters';
                }
                break;
        }
    }

    // Update field styling
    if (isValid) {
        $field.removeClass('is-invalid').addClass('is-valid');
        $field.next('.invalid-feedback').remove();
    } else {
        $field.removeClass('is-valid').addClass('is-invalid');
        
        // Add error message if not exists
        if (!$field.next('.invalid-feedback').length) {
            $field.after(`<div class="invalid-feedback">${errorMessage}</div>`);
        }
    }

    return isValid;
}

function validateCompleteForm() {
    let isValid = true;
    
    $('input[required], select[required]').each(function() {
        if (!validateField($(this))) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * UI Helper functions
 */
function showLoading(message = 'Loading...') {
    const loadingHtml = `
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content">
                <div class="spinner"></div>
                <h4>${message}</h4>
                <p>Please wait while we process your request.</p>
            </div>
        </div>
    `;
    
    if (!$('#loadingOverlay').length) {
        $('body').append(loadingHtml);
    }
    
    $('#loadingOverlay').fadeIn(300);
}

function hideLoading() {
    $('#loadingOverlay').fadeOut(300, function() {
        $(this).remove();
    });
}

function showAlert(message, type = 'info', duration = 5000) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('body').append(alertHtml);
    
    // Auto remove after duration
    setTimeout(function() {
        $('.alert').last().fadeOut(function() {
            $(this).remove();
        });
    }, duration);
}

/**
 * Table and data functions
 */
function filterTable(searchTerm) {
    $('table tbody tr').each(function() {
        const rowText = $(this).text().toLowerCase();
        if (rowText.indexOf(searchTerm) === -1) {
            $(this).hide();
        } else {
            $(this).show();
        }
    });
}

function applyFilters() {
    const statusFilter = $('#statusFilter').val();
    const riskFilter = $('#riskFilter').val();
    
    $('table tbody tr').each(function() {
        let showRow = true;
        
        if (statusFilter && !$(this).find('.badge').text().includes(statusFilter)) {
            showRow = false;
        }
        
        if (riskFilter && !$(this).text().toLowerCase().includes(riskFilter.toLowerCase())) {
            showRow = false;
        }
        
        if (showRow) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

function exportTableData() {
    const table = document.querySelector('table');
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length - 1; j++) { // Exclude last column (actions)
            row.push(cols[j].innerText.replace(/,/g, ';'));
        }
        csv.push(row.join(','));
    }
    
    downloadCSV(csv.join('\n'), 'finloan_data.csv');
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/**
 * Animation functions
 */
function animateProgressBars() {
    $('.progress-bar').each(function() {
        const $bar = $(this);
        const percent = $bar.data('percent') || $bar.attr('aria-valuenow');
        
        $bar.css('width', '0%');
        $bar.animate({ width: percent + '%' }, 1500, 'easeOutExpo');
    });
}

function animateCounters() {
    $('.counter').each(function() {
        const $counter = $(this);
        const target = parseInt($counter.text());
        
        $counter.text('0');
        $counter.animate({ Counter: target }, {
            duration: 2000,
            easing: 'easeOutExpo',
            step: function(now) {
                $counter.text(Math.ceil(now));
            }
        });
    });
}

function typeWriter(element, text, speed = 100) {
    const $element = $(element);
    let i = 0;
    
    function type() {
        if (i < text.length) {
            $element.text($element.text() + text.charAt(i));
            i++;
            setTimeout(type, speed);
        }
    }
    
    $element.text('');
    type();
}

/**
 * Utility functions
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatPercentage(value, decimals = 1) {
    return (value * 100).toFixed(decimals) + '%';
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Risk Assessment Calculator
 */
function calculateRiskScore(applicationData) {
    let score = 0;
    
    // Credit History (40% weight)
    if (applicationData.credit_history === 'Yes') score += 40;
    
    // Education (20% weight)
    if (applicationData.education === 'Graduate') score += 20;
    
    // Income factors (25% weight)
    const totalIncome = parseInt(applicationData.applicant_income) + parseInt(applicationData.coapplicant_income || 0);
    if (totalIncome > 8000) score += 25;
    else if (totalIncome > 5000) score += 15;
    else if (totalIncome > 3000) score += 10;
    
    // Loan to Income Ratio (10% weight)
    const loanAmount = parseInt(applicationData.loan_amount) * 1000;
    const loanToIncomeRatio = loanAmount / totalIncome;
    if (loanToIncomeRatio < 3) score += 10;
    else if (loanToIncomeRatio < 5) score += 5;
    
    // Employment Status (5% weight)
    if (applicationData.self_employed === 'No') score += 5;
    
    return Math.min(score, 100);
}

function getRiskLevel(score) {
    if (score >= 70) return { level: 'Low', class: 'success', color: '#28a745' };
    if (score >= 50) return { level: 'Medium', class: 'warning', color: '#ffc107' };
    return { level: 'High', class: 'danger', color: '#dc3545' };
}

/**
 * Local Storage functions
 */
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (e) {
        console.error('Error saving to localStorage:', e);
        return false;
    }
}

function getFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return null;
    }
}

/**
 * Error handling
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'danger');
});

// jQuery easing extension for smooth animations
$.extend($.easing, {
    easeOutExpo: function(x, t, b, c, d) {
        return (t == d) ? b + c : c * (-Math.pow(2, -10 * t / d) + 1) + b;
    },
    easeInOutExpo: function(x, t, b, c, d) {
        if (t == 0) return b;
        if (t == d) return b + c;
        if ((t /= d / 2) < 1) return c / 2 * Math.pow(2, 10 * (t - 1)) + b;
        return c / 2 * (-Math.pow(2, -10 * --t) + 2) + b;
    }
});

// Console welcome message
console.log(`
🚀 FinLoan AI - Loan Prediction Platform
================================================
Version: 1.0.0
Built with: Django + Bootstrap + jQuery + ML
Features: Real-time predictions, Risk analysis
================================================
`);

// Export functions for global access
window.FinLoanAI = {
    showLoading,
    hideLoading,
    showAlert,
    calculateRiskScore,
    getRiskLevel,
    formatCurrency,
    formatPercentage,
    saveToLocalStorage,
    getFromLocalStorage
};
