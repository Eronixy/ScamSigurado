document.addEventListener("DOMContentLoaded", function () {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;

    darkModeToggle.addEventListener('click', () => {
        html.classList.toggle('dark');
    });

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.getElementById('imagePreview');
    const fileName = document.getElementById('fileName');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeText = document.getElementById('analyzeText');
    const clearImageBtn = document.getElementById('clearImageBtn');

    // NEW: Get the new content containers within the dropZone
    const dropZoneContent = document.getElementById('dropZoneContent');
    const imagePreviewContent = document.getElementById('imagePreviewContent');

    // Event listeners for the dropZone
    dropZone.addEventListener('click', () => {
        // Only trigger file input click if no image is currently displayed
        if (imagePreviewContent.classList.contains('hidden')) {
            fileInput.click();
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-custom-primary');
    });

    dropZone.addEventListener('dragleave', () => {
        // Only remove border-custom-primary if no image is currently displayed
        if (imagePreviewContent.classList.contains('hidden')) {
            dropZone.classList.remove('border-custom-primary');
        }
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        // The border-custom-primary class will be removed in handleFile
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // Event listener for file input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Function to handle file processing and UI update
    function handleFile(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                fileName.textContent = file.name;
                
                // Toggle visibility: hide initial drop zone content, show image preview
                dropZoneContent.classList.add('hidden');
                imagePreviewContent.classList.remove('hidden');
                dropZone.classList.remove('border-custom-primary'); // Remove dragover border on successful drop

                analyzeBtn.disabled = false;
                analyzeText.textContent = 'Analyze Screenshot';
                
                // Hide results and feedback sections when a new image is selected
                const resultsSection = document.getElementById('resultsSection');
                const feedbackSuccess = document.getElementById('feedbackSuccess');
                const reportSuccess = document.getElementById('reportSuccess');
                const incorrectFeedback = document.getElementById('incorrectFeedback');

                if (resultsSection) resultsSection.classList.add('hidden');
                if (feedbackSuccess) feedbackSuccess.classList.add('hidden');
                if (reportSuccess) reportSuccess.classList.add('hidden');
                if (incorrectFeedback) incorrectFeedback.classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }
    }

    // Clear Image Button functionality
    clearImageBtn.addEventListener('click', () => {
        fileInput.value = ''; // Clear the selected file
        imagePreview.src = ''; // Clear the image preview
        fileName.textContent = ''; // Clear the file name
        
        // Toggle visibility back: hide image preview, show initial drop zone content
        imagePreviewContent.classList.add('hidden');
        dropZoneContent.classList.remove('hidden');

        analyzeBtn.disabled = true; // Disable the analyze button
        analyzeText.textContent = 'Select an image to analyze'; // Reset button text
        
        // Hide results and feedback sections
        const resultsSection = document.getElementById('resultsSection');
        const feedbackSuccess = document.getElementById('feedbackSuccess');
        const reportSuccess = document.getElementById('reportSuccess');
        const incorrectFeedback = document.getElementById('incorrectFeedback');

        if (resultsSection) resultsSection.classList.add('hidden');
        if (feedbackSuccess) feedbackSuccess.classList.add('hidden');
        if (reportSuccess) reportSuccess.classList.add('hidden');
        if (incorrectFeedback) incorrectFeedback.classList.add('hidden');

        dropZone.classList.remove('border-custom-primary'); // Ensure default border state
    });

    // Advanced Settings Toggle
    const advancedToggle = document.getElementById('advancedToggle');
    const advancedSettings = document.getElementById('advancedSettings');
    const advancedArrow = document.getElementById('advancedArrow');

    if (advancedToggle && advancedSettings && advancedArrow) {
        advancedToggle.addEventListener('click', () => {
            advancedSettings.classList.toggle('hidden');
            advancedArrow.classList.toggle('rotate-180');
        });
    }

    // Weight Sliders
    const textWeight = document.getElementById('textWeight');
    const cnnWeight = document.getElementById('cnnWeight');
    const textWeightValue = document.getElementById('textWeightValue');
    const cnnWeightValue = document.getElementById('cnnWeightValue');

    if (textWeight && cnnWeight && textWeightValue && cnnWeightValue) {
        textWeight.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            textWeightValue.textContent = value.toFixed(1);
            cnnWeight.value = (1 - value).toFixed(1);
            cnnWeightValue.textContent = (1 - value).toFixed(1);
        });

        cnnWeight.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            cnnWeightValue.textContent = value.toFixed(1);
            textWeight.value = (1 - value).toFixed(1);
            textWeightValue.textContent = (1 - value).toFixed(1);
        });
    }

    // Modals
    const analysisModal = document.getElementById('analysisModal');
    const analysisModalContent = document.getElementById('analysisModalContent');
    const successModal = document.getElementById('successModal');
    const successModalContent = document.getElementById('successModalContent');

    function showModal(modal, content) {
        if (modal && content) {
            modal.classList.remove('hidden');
            setTimeout(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }, 10);
        }
    }

    function hideModal(modal, content) {
        if (modal && content) {
            content.classList.remove('scale-100', 'opacity-100');
            content.classList.add('scale-95', 'opacity-0');

            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            if (analyzeBtn.disabled) return;

            const steps = ['step1', 'step2', 'step3', 'step4'];
            steps.forEach(stepId => {
                const step = document.getElementById(stepId);
                if (step) {
                    step.classList.add('opacity-50');
                    step.classList.remove('text-custom-primary', 'font-medium');
                }
            });

            const successIcon = document.querySelector('#successModalContent .w-16');
            if (successIcon) {
                successIcon.classList.remove('scale-100');
                successIcon.classList.add('scale-0');
            }

            showModal(analysisModal, analysisModalContent);

            let currentStep = 0;

            const stepInterval = setInterval(() => {
                if (currentStep < steps.length) {
                    const stepElement = document.getElementById(steps[currentStep]);
                    if (stepElement) {
                        stepElement.classList.remove('opacity-50');
                        stepElement.classList.add('text-custom-primary', 'font-medium');
                    }
                    currentStep++;
                } else {
                    clearInterval(stepInterval);
                }
            }, 700);

            setTimeout(() => {
                hideModal(analysisModal, analysisModalContent);

                setTimeout(() => {
                    showModal(successModal, successModalContent);

                    setTimeout(() => {
                        const successIconElement = document.querySelector('#successModalContent .w-16');
                        if (successIconElement) {
                            successIconElement.classList.remove('scale-0');
                            successIconElement.classList.add('scale-100');
                        }
                    }, 200);
                }, 300);

                showResults();
            }, 3000);
        });
    }

    const viewResultsBtn = document.getElementById('viewResultsBtn');
    const resultsSection = document.getElementById('resultsSection');

    if (viewResultsBtn && resultsSection) {
        viewResultsBtn.addEventListener('click', () => {
            hideModal(successModal, successModalContent);
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }, 300);
        });
    }

    function showResults() {
        const isScam = Math.random() > 0.4;
        const confidence = Math.random() * 40 + 60;
        const textConf = Math.random() * 100;
        const imageConf = Math.random() * 100;

        const mainResult = document.getElementById('mainResult');
        const resultIcon = document.getElementById('resultIcon');
        const resultTitle = document.getElementById('resultTitle');
        const resultDescription = document.getElementById('resultDescription');
        const confidenceBar = document.getElementById('confidenceBar');
        const confidenceText = document.getElementById('confidenceText');
        const textConfidence = document.getElementById('textConfidence');
        const imageConfidence = document.getElementById('imageConfidence');

        if (!mainResult || !resultIcon || !resultTitle || !resultDescription || !confidenceBar || !confidenceText || !textConfidence || !imageConfidence) {
            console.error("One or more result elements not found.");
            return;
        }

        if (isScam) {
            mainResult.className = 'text-center p-6 rounded-lg border-2 border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20';
            resultIcon.innerHTML = `
                <svg class="w-16 h-16 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 19c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>`;
            resultTitle.textContent = 'SCAM DETECTED';
            resultTitle.className = 'text-2xl font-bold mb-2 text-red-600';
            resultDescription.textContent = 'This screenshot shows potential scam indicators. Exercise caution and verify before taking any action.';
            confidenceBar.className = 'h-3 rounded-full transition-all duration-500 bg-red-500';
        } else {
            mainResult.className = 'text-center p-6 rounded-lg border-2 border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20';
            resultIcon.innerHTML = `
                <svg class="w-16 h-16 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>`;
            resultTitle.textContent = 'LEGITIMATE';
            resultTitle.className = 'text-2xl font-bold mb-2 text-green-600';
            resultDescription.textContent = 'This screenshot appears to be legitimate with no obvious scam indicators detected.';
            confidenceBar.className = 'h-3 rounded-full transition-all duration-500 bg-green-500';
        }

        confidenceBar.style.width = confidence + '%';
        confidenceText.textContent = confidence.toFixed(1) + '%';
        textConfidence.textContent = textConf.toFixed(1) + '%';
        imageConfidence.textContent = imageConf.toFixed(1) + '%';

        resultsSection.classList.remove('hidden');
    }

    const correctBtn = document.getElementById('correctBtn');
    const incorrectBtn = document.getElementById('incorrectBtn');
    const feedbackButtons = document.getElementById('feedbackButtons');
    const incorrectFeedback = document.getElementById('incorrectFeedback');
    const feedbackSuccess = document.getElementById('feedbackSuccess');
    const submitFeedback = document.getElementById('submitFeedback');

    if (correctBtn && feedbackButtons && feedbackSuccess) {
        correctBtn.addEventListener('click', () => {
            feedbackButtons.classList.add('hidden');
            feedbackSuccess.classList.remove('hidden');
            feedbackSuccess.textContent = 'Thank you for confirming! This helps improve our model accuracy.';
        });
    }

    if (incorrectBtn && feedbackButtons && incorrectFeedback) {
        incorrectBtn.addEventListener('click', () => {
            feedbackButtons.classList.add('hidden');
            incorrectFeedback.classList.remove('hidden');
        });
    }

    if (submitFeedback && incorrectFeedback && feedbackSuccess) {
        submitFeedback.addEventListener('click', () => {
            const classification = document.getElementById('correctClassification');
            const comments = document.getElementById('feedbackComments');

            if (classification && classification.value) {
                incorrectFeedback.classList.add('hidden');
                feedbackSuccess.classList.remove('hidden');
                feedbackSuccess.textContent = 'Thank you for the correction! This helps improve our model accuracy.';
            } else {
                alert('Please select the correct classification.');
            }
        });
    }

    const reportScam = document.getElementById('reportScam');
    const reportSuccess = document.getElementById('reportSuccess');

    if (reportScam && reportSuccess) {
        reportScam.addEventListener('click', () => {
            const scamType = document.getElementById('scamType');
            const description = document.getElementById('scamDescription');

            if (scamType && scamType.value && description && description.value) {
                reportSuccess.classList.remove('hidden');
                reportScam.disabled = true;
                reportScam.textContent = 'Report Submitted ✓';
                reportScam.className = 'bg-gray-400 text-white py-2 px-4 rounded-lg font-medium cursor-not-allowed';
            } else {
                alert('Please fill in all required fields.');
            }
        });
    }

    // Carousel functionality
    const carousel = document.getElementById('carousel');
    const carouselTrack = document.getElementById('carouselTrack'); // Added this ID to the inner div
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carouselDotsContainer = document.getElementById('carouselDots'); // Container for dots
    
    let currentSlide = 0;
    const totalSlides = 5; // Ensure this matches the number of slides in your HTML

    const createCarouselDots = () => {
        if (!carouselDotsContainer) return;
        carouselDotsContainer.innerHTML = ''; // Clear existing dots
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('span');
            dot.classList.add('carousel-dot', 'w-3', 'h-3', 'rounded-full', 'bg-gray-300', 'dark:bg-gray-600', 'cursor-pointer', 'transition-colors', 'duration-300');
            dot.addEventListener('click', () => {
                currentSlide = i;
                updateCarousel();
            });
            carouselDotsContainer.appendChild(dot);
        }
    }

    function updateCarousel() {
        if (!carouselTrack || !carouselDotsContainer) return;
        const translateX = -currentSlide * 100;
        carouselTrack.style.transform = `translateX(${translateX}%)`; // Apply transform to carouselTrack

        const dots = carouselDotsContainer.querySelectorAll('.carousel-dot'); // Select dots within the container
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.remove('bg-gray-300', 'dark:bg-gray-600'); // Remove inactive state
                dot.classList.add('bg-scam-primary'); // Add active state
            } else {
                dot.classList.remove('bg-scam-primary'); // Remove active state
                dot.classList.add('bg-gray-300', 'dark:bg-gray-600'); // Add inactive state
            }
        });
    }

    // Initialize dots and first slide on load
    createCarouselDots();
    updateCarousel(); // Show the first slide and update dots initially

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentSlide = (currentSlide === 0) ? totalSlides - 1 : currentSlide - 1;
            updateCarousel();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentSlide = (currentSlide === totalSlides - 1) ? 0 : currentSlide + 1;
            updateCarousel();
        });
    }

    // Auto-advance carousel
    setInterval(() => {
        currentSlide = (currentSlide === totalSlides - 1) ? 0 : currentSlide + 1;
        updateCarousel();
    }, 5000);
});