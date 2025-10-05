// Main JavaScript for Questionnaire Management System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Form validation enhancements
    $('form').on('submit', function() {
        showLoading();
    });

    // Questionnaire Builder Functions
    initQuestionnaireBuilder();
    
    // Response Form Functions
    initResponseForm();
    
    // Chart Functions
    initCharts();
    
    // Search functionality
    initSearch();
});

// Loading Spinner Functions
function showLoading() {
    $('.loading-backdrop').show();
    $('.loading-spinner').show();
}

function hideLoading() {
    $('.loading-backdrop').hide();
    $('.loading-spinner').hide();
}

// Questionnaire Builder Functions
function initQuestionnaireBuilder() {
    // Handle question type changes
    $(document).on('change', '.question-type-select', function() {
        const questionType = $(this).val();
        const questionContainer = $(this).closest('.question-item');
        const optionsContainer = questionContainer.find('.choice-options');
        
        if (questionType === 'single_choice' || questionType === 'multiple_choice') {
            optionsContainer.show();
            generateOptionInputs(optionsContainer, 2); // Start with 2 options
        } else {
            optionsContainer.hide();
        }
    });
    
    // Add new option
    $(document).on('click', '.add-option-btn', function() {
        const optionsContainer = $(this).closest('.choice-options').find('.options-list');
        const optionCount = optionsContainer.children().length + 1;
        
        const newOption = $(`
            <div class="input-group mb-2 option-input">
                <span class="input-group-text">Option ${optionCount}</span>
                <input type="text" class="form-control option-text" placeholder="Enter option text">
                <button type="button" class="btn btn-outline-danger remove-option-btn">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `);
        
        optionsContainer.append(newOption);
        newOption.addClass('fade-in');
    });
    
    // Remove option
    $(document).on('click', '.remove-option-btn', function() {
        const optionsContainer = $(this).closest('.options-list');
        $(this).closest('.option-input').fadeOut(300, function() {
            $(this).remove();
            // Renumber remaining options
            optionsContainer.find('.option-input').each(function(index) {
                $(this).find('.input-group-text').text(`Option ${index + 1}`);
            });
        });
    });
    
    // Add new question
    $('#add-question-btn').on('click', function() {
        const questionnaireId = $(this).data('questionnaire-id');
        const questionCount = $('.question-item').length + 1;
        
        const newQuestion = createQuestionHTML(questionCount);
        newQuestion.attr('data-questionnaire-id', questionnaireId);
        $('#questions-container').append(newQuestion);
        newQuestion.addClass('fade-in');
    });
    
    // Save question
    $(document).on('click', '.save-question-btn', function() {
        saveQuestion($(this).closest('.question-item'));
    });
    
    // Delete question
    $(document).on('click', '.delete-question-btn', function() {
        const questionItem = $(this).closest('.question-item');
        const questionId = questionItem.data('question-id');
        
        if (confirm('Are you sure you want to delete this question?')) {
            if (questionId) {
                deleteQuestion(questionId, questionItem);
            } else {
                questionItem.fadeOut(300, function() {
                    $(this).remove();
                });
            }
        }
    });
}

function generateOptionInputs(container, count = 2) {
    const optionsList = container.find('.options-list');
    optionsList.empty();
    
    for (let i = 1; i <= count; i++) {
        const option = $(`
            <div class="input-group mb-2 option-input">
                <span class="input-group-text">Option ${i}</span>
                <input type="text" class="form-control option-text" placeholder="Enter option text">
                <button type="button" class="btn btn-outline-danger remove-option-btn">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `);
        optionsList.append(option);
    }
    
    // Show the add option button
    container.find('.add-option-btn').show();
}

function createQuestionHTML(order) {
    return $(`
        <div class="question-item card mb-3" data-order="${order}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="card-title mb-0">
                        <i class="bi bi-grip-vertical drag-handle"></i>
                        Question ${order}
                    </h6>
                    <div>
                        <button type="button" class="btn btn-success btn-sm save-question-btn">
                            <i class="bi bi-save"></i> Save
                        </button>
                        <button type="button" class="btn btn-danger btn-sm delete-question-btn">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Question Text</label>
                    <textarea class="form-control question-text" rows="3" placeholder="Enter your question"></textarea>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Question Type</label>
                        <select class="form-select question-type-select">
                            <option value="single_choice">Single Choice</option>
                            <option value="multiple_choice">Multiple Choice</option>
                            <option value="open_ended">Open-ended Text</option>
                            <option value="scale">Scale (1-5)</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <div class="form-check mt-4">
                            <input class="form-check-input question-required" type="checkbox" checked>
                            <label class="form-check-label">Required</label>
                        </div>
                    </div>
                </div>
                
                <div class="choice-options" style="display: block;">
                    <label class="form-label">Answer Options</label>
                    <div class="options-list"></div>
                    <button type="button" class="btn btn-outline-primary btn-sm add-option-btn">
                        <i class="bi bi-plus-circle"></i> Add Option
                    </button>
                </div>
            </div>
        </div>
    `);
}

// Response Form Functions - Enhanced for Multiple Choice
function initResponseForm() {
    // Auto-save responses (optional feature)
    let saveTimeout;
    $('input, textarea, select').on('change', function() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(function() {
            // Implement auto-save functionality here
            console.log('Auto-saving response...');
        }, 2000);
    });
    
    // Progress tracking
    updateProgress();
    $('input, textarea, select').on('change', updateProgress);
    
    // Enhanced checkbox behavior for multiple choice
    $('.form-check-input[type="checkbox"]').on('change', function() {
        const questionContainer = $(this).closest('.question-container');
        const questionId = questionContainer.data('question-id');
        const selectedOptions = questionContainer.find('input[type="checkbox"]:checked');
        
        console.log(`Question ${questionId}: ${selectedOptions.length} options selected`);
        
        // Visual feedback for multiple selections
        if (selectedOptions.length > 1) {
            questionContainer.find('.question-text').addClass('text-success');
        } else {
            questionContainer.find('.question-text').removeClass('text-success');
        }
    });
    
    // Form submission with validation
    $('#response-form').on('submit', function(e) {
        if (!validateResponseForm()) {
            e.preventDefault();
        }
    });
}

function updateProgress() {
    const totalQuestions = $('.question-container').length;
    const answeredQuestions = $('.question-container').filter(function() {
        const inputs = $(this).find('input, textarea, select');
        return inputs.filter(function() {
            return $(this).val() !== '' && $(this).val() !== null;
        }).length > 0;
    }).length;
    
    const progress = totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
    $('#progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
    $('#progress-text').text(`${answeredQuestions} of ${totalQuestions} questions answered`);
}

function validateResponseForm() {
    let isValid = true;
    
    $('.question-container').each(function() {
        const isRequired = $(this).data('required') === true;
        const hasAnswer = $(this).find('input:checked, textarea:not(:empty), select:not([value=""])').length > 0;
        
        if (isRequired && !hasAnswer) {
            $(this).addClass('border border-danger');
            isValid = false;
        } else {
            $(this).removeClass('border border-danger');
        }
    });
    
    if (!isValid) {
        alert('Please answer all required questions before submitting.');
    }
    
    return isValid;
}

// Chart Functions
function initCharts() {
    // Initialize charts if chart canvas elements exist
    $('.chart-canvas').each(function() {
        const chartType = $(this).data('chart-type');
        const chartData = $(this).data('chart-data');
        
        if (chartData) {
            createChart(this, chartType, chartData);
        }
    });
}

function createChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    
    const config = {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed} responses`;
                        }
                    }
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// Search Functions
function initSearch() {
    // Live search functionality
    let searchTimeout;
    $('#search-input').on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val();
        
        searchTimeout = setTimeout(function() {
            if (query.length >= 3 || query.length === 0) {
                performSearch(query);
            }
        }, 500);
    });
}

function performSearch(query) {
    // Implement live search functionality
    console.log('Searching for:', query);
}

// API Helper Functions
function saveQuestion(questionItem) {
    // Get questionnaire ID from the hidden input or data attribute
    const questionnaireId = $('#questionnaire-id').val() || questionItem.closest('[data-questionnaire-id]').data('questionnaire-id');
    
    if (!questionnaireId) {
        showAlert('Questionnaire ID not found. Please refresh the page.', 'danger');
        return;
    }
    
    // Validate required fields
    const questionText = questionItem.find('.question-text').val().trim();
    if (!questionText) {
        showAlert('Question text is required.', 'warning');
        questionItem.find('.question-text').focus();
        return;
    }
    
    const questionData = {
        questionnaire_id: parseInt(questionnaireId),
        question_text: questionText,
        question_type: questionItem.find('.question-type-select').val(),
        is_required: questionItem.find('.question-required').is(':checked'),
        order: questionItem.data('order') || 0
    };
    
    // Collect options for choice questions
    if (questionData.question_type === 'single_choice' || questionData.question_type === 'multiple_choice') {
        const options = [];
        questionItem.find('.option-text').each(function() {
            const optionText = $(this).val().trim();
            if (optionText) {
                options.push(optionText);
            }
        });
        
        if (options.length < 2) {
            showAlert('Please provide at least 2 options for choice questions.', 'warning');
            return;
        }
        
        questionData.options = options;
    }
    
    const questionId = questionItem.data('question-id');
    const method = questionId ? 'PUT' : 'POST';
    const url = questionId ? `/api/questions/${questionId}` : '/api/questions';
    
    console.log('Saving question:', questionData); // Debug log
    
    showLoading();
    
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(questionData),
        success: function(response) {
            hideLoading();
            questionItem.data('question-id', response.id);
            questionItem.addClass('border border-success');
            
            setTimeout(function() {
                questionItem.removeClass('border border-success');
            }, 2000);
            
            showAlert('Question saved successfully!', 'success');
        },
        error: function(xhr, status, error) {
            hideLoading();
            console.error('AJAX Error:', xhr.responseText, status, error); // Debug log
            
            let errorMessage = 'Failed to save question';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            } else if (xhr.responseText) {
                errorMessage = xhr.responseText;
            } else if (error) {
                errorMessage = error;
            }
            
            showAlert(errorMessage, 'danger');
        }
    });
}

function deleteQuestion(questionId, questionItem) {
    showLoading();
    
    $.ajax({
        url: `/api/questions/${questionId}`,
        method: 'DELETE',
        success: function() {
            hideLoading();
            questionItem.fadeOut(300, function() {
                $(this).remove();
            });
            showAlert('Question deleted successfully!', 'success');
        },
        error: function(xhr) {
            hideLoading();
            const error = xhr.responseJSON ? xhr.responseJSON.error : 'Failed to delete question';
            showAlert(error, 'danger');
        }
    });
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('.container').first().prepend(alert);
    
    setTimeout(function() {
        alert.fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}