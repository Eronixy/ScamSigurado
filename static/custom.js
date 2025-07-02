document.addEventListener("DOMContentLoaded", function () {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;

    darkModeToggle.addEventListener('click', () => {
        html.classList.toggle('dark');
    });

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const fileName = document.getElementById('fileName');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeText = document.getElementById('analyzeText');
    let currentFile = null;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-custom-primary');
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-custom-primary');
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-custom-primary');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

        function handleFile(file) {
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                    fileName.textContent = file.name;
                    previewContainer.classList.remove('hidden');
                    analyzeBtn.disabled = false;
                    analyzeText.textContent = 'Analyze Screenshot';
                };
                reader.readAsDataURL(file);
            }
        }

        const clearImageBtn = document.getElementById('clearImageBtn'); // Get the clear button

        // New: Clear Image Button functionality
        clearImageBtn.addEventListener('click', () => {
            fileInput.value = ''; // Clear the selected file
            imagePreview.src = ''; // Clear the image preview
            fileName.textContent = ''; // Clear the file name
            previewContainer.classList.add('hidden'); // Hide the preview container
            analyzeBtn.disabled = true; // Disable the analyze button
            analyzeText.textContent = 'Select an image to analyze'; // Reset button text
            resultsSection.classList.add('hidden'); // Hide results section if visible
            feedbackSuccess.classList.add('hidden'); // Hide feedback success message
            reportSuccess.classList.add('hidden'); // Hide report success message
            incorrectFeedback.classList.add('hidden'); // Hide incorrect feedback section
        });

    const advancedToggle = document.getElementById('advancedToggle');
    const advancedSettings = document.getElementById('advancedSettings');
    const advancedArrow = document.getElementById('advancedArrow');

    advancedToggle.addEventListener('click', () => {
        advancedSettings.classList.toggle('hidden');
        advancedArrow.classList.toggle('rotate-180');
    });

    const textWeight = document.getElementById('textWeight');
    const cnnWeight = document.getElementById('cnnWeight');
    const textWeightValue = document.getElementById('textWeightValue');
    const cnnWeightValue = document.getElementById('cnnWeightValue');

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

    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');

    function showModal(modalId, contentId) {
        const modal = document.getElementById(modalId);
        const content = document.getElementById(contentId);

        modal.classList.remove('hidden');
        setTimeout(() => {
            content.classList.remove('scale-95', 'opacity-0');
            content.classList.add('scale-100', 'opacity-100');
        }, 10);
    }

    function hideModal(modalId, contentId) {
        const content = document.getElementById(contentId);
        content.classList.remove('scale-100', 'opacity-100');
        content.classList.add('scale-95', 'opacity-0');

        setTimeout(() => {
            document.getElementById(modalId).classList.add('hidden');
        }, 300);
    }

    // Main analysis function - now makes actual API call
    analyzeBtn.addEventListener('click', async () => {
        if (analyzeBtn.disabled || !currentFile) return;

        // Reset and show loading state
        const steps = ['step1', 'step2', 'step3', 'step4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            step.classList.add('opacity-50');
            step.classList.remove('text-custom-primary', 'font-medium');
        });

        const successIcon = document.querySelector('#successModalContent .w-16');
        successIcon.classList.remove('scale-100');
        successIcon.classList.add('scale-0');

        showModal('analysisModal', 'analysisModalContent');

        let currentStep = 0;
        const stepInterval = setInterval(() => {
            if (currentStep < steps.length) {
                document.getElementById(steps[currentStep]).classList.remove('opacity-50');
                document.getElementById(steps[currentStep]).classList.add('text-custom-primary', 'font-medium');
                currentStep++;
            } else {
                clearInterval(stepInterval);
            }
        }, 700);

        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('screenshot', currentFile);
            formData.append('text_model', document.getElementById('textModel').value);
            formData.append('cnn_model', document.getElementById('cnnModel').value);
            formData.append('text_weight', textWeight.value);
            formData.append('cnn_weight', cnnWeight.value);

            // Make API call to Flask backend
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            // Clear the step animation
            clearInterval(stepInterval);

            // PROPER ERROR HANDLING - Check both response status AND result.success
            if (!response.ok || !result.success) {
                throw new Error(result.error || `Server error: ${response.status}`);
            }

            // Only proceed if truly successful
            setTimeout(() => {
                hideModal('analysisModal', 'analysisModalContent');

                setTimeout(() => {
                    showModal('successModal', 'successModalContent');

                    setTimeout(() => {
                        const successIcon = document.querySelector('#successModalContent .w-16');
                        successIcon.classList.remove('scale-0');
                        successIcon.classList.add('scale-100');
                    }, 200);
                }, 300);

                // Show results with actual data from backend
                showResults(result);
            }, 3000);

        } catch (error) {
            console.error('Analysis error:', error);

            // Clear the step animation on error
            clearInterval(stepInterval);

            // Hide the analysis modal
            hideModal('analysisModal', 'analysisModalContent');

            // Show error message
            setTimeout(() => {
                alert(`Analysis failed: ${error.message}`);

                // Reset analyze button
                analyzeBtn.disabled = false;
                analyzeText.textContent = 'Analyze Screenshot';
            }, 300);
        }
    });

    document.getElementById('viewResultsBtn').addEventListener('click', () => {
        hideModal('successModal', 'successModalContent');
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 300);
    });




    function showResults(result) {
        const isScam = result.is_scam;
        const confidence = result.confidence;
        const textConf = result.text_confidence;
        const imageConf = result.image_confidence;

        const mainResult = document.getElementById('mainResult');
        const resultIcon = document.getElementById('resultIcon');
        const resultTitle = document.getElementById('resultTitle');
        const resultDescription = document.getElementById('resultDescription');
        const confidenceBar = document.getElementById('confidenceBar');
        const confidenceText = document.getElementById('confidenceText');
        const textConfidence = document.getElementById('textConfidence');
        const imageConfidence = document.getElementById('imageConfidence');

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

    correctBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feedback_type: 'correct',
                    timestamp: new Date().toISOString()
                })
            });

            if (response.ok) {
                feedbackButtons.classList.add('hidden');
                feedbackSuccess.classList.remove('hidden');
                feedbackSuccess.textContent = 'Thank you for confirming! This helps improve our model accuracy.';
            }
        } catch (error) {
            console.error('Feedback error:', error);
        }
    });

    incorrectBtn.addEventListener('click', () => {
        feedbackButtons.classList.add('hidden');
        incorrectFeedback.classList.remove('hidden');
    });

    submitFeedback.addEventListener('click', async () => {
        const classification = document.getElementById('correctClassification').value;
        const comments = document.getElementById('feedbackComments').value;

        if (classification) {
            try {
                const response = await fetch('/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        feedback_type: 'incorrect',
                        correct_classification: classification,
                        comments: comments,
                        timestamp: new Date().toISOString()
                    })
                });

                if (response.ok) {
                    incorrectFeedback.classList.add('hidden');
                    feedbackSuccess.classList.remove('hidden');
                    feedbackSuccess.textContent = 'Thank you for the correction! This helps improve our model accuracy.';
                }
            } catch (error) {
                console.error('Feedback error:', error);
            }
        } else {
            alert('Please select the correct classification.');
        }
    });

    const reportScam = document.getElementById('reportScam');
    const reportSuccess = document.getElementById('reportSuccess');

    reportScam.addEventListener('click', async () => {
        const scamType = document.getElementById('scamType').value;
        const description = document.getElementById('scamDescription').value;

        if (scamType && description) {
            try {
                const response = await fetch('/report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        scam_type: scamType,
                        description: description,
                        timestamp: new Date().toISOString()
                    })
                });

                if (response.ok) {
                    reportSuccess.classList.remove('hidden');
                    reportScam.disabled = true;
                    reportScam.textContent = 'Report Submitted ✓';
                    reportScam.className = 'bg-gray-400 text-white py-2 px-4 rounded-lg font-medium cursor-not-allowed';
                }
            } catch (error) {
                console.error('Report error:', error);
            }
        } else {
            alert('Please fill in all required fields.');
        }
    });

    const carousel = document.getElementById('carousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carouselDots = document.querySelectorAll('.carousel-dot');
    let currentSlide = 0;
    const totalSlides = 5;

    function updateCarousel() {
        const translateX = -currentSlide * 100;
        carousel.style.transform = `translateX(${translateX}%)`;

        carouselDots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.className = 'carousel-dot w-3 h-3 rounded-full bg-custom-primary';
            } else {
                dot.className = 'carousel-dot w-3 h-3 rounded-full bg-gray-300 dark:bg-gray-600';
            }
        });
    }

    prevBtn.addEventListener('click', () => {
        currentSlide = currentSlide === 0 ? totalSlides - 1 : currentSlide - 1;
        updateCarousel();
    });

    nextBtn.addEventListener('click', () => {
        currentSlide = currentSlide === totalSlides - 1 ? 0 : currentSlide + 1;
        updateCarousel();
    });

    carouselDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentSlide = index;
            updateCarousel();
        });
    });

    setInterval(() => {
        currentSlide = currentSlide === totalSlides - 1 ? 0 : currentSlide + 1;
        updateCarousel();
    }, 5000);
});