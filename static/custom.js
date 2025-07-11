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

    const dropZoneContent = document.getElementById('dropZoneContent');
    const imagePreviewContent = document.getElementById('imagePreviewContent');
    let currentFile = null;

    dropZone.addEventListener('click', () => {
        if (imagePreviewContent.classList.contains('hidden')) {
            fileInput.click();
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-custom-primary');
    });

    dropZone.addEventListener('dragleave', () => {
        if (imagePreviewContent.classList.contains('hidden')) {
            dropZone.classList.remove('border-custom-primary');
        }
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
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
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) resultsSection.classList.add('hidden');

            const featureContainer = document.getElementById('featureImportanceContainer');
            if (featureContainer) {
                featureContainer.remove();
            }

            const textContainer = document.getElementById('extractedTextContainer');
            if (textContainer) {
                textContainer.remove();
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                fileName.textContent = file.name;

                dropZoneContent.classList.add('hidden');
                imagePreviewContent.classList.remove('hidden');
                dropZone.classList.remove('border-custom-primary');

                analyzeBtn.disabled = false;
                analyzeText.textContent = 'Analyze Screenshot';
                currentFile = file;

                const feedbackSuccess = document.getElementById('feedbackSuccess');
                const reportSuccess = document.getElementById('reportSuccess');
                const incorrectFeedback = document.getElementById('incorrectFeedback');

                if (feedbackSuccess) feedbackSuccess.classList.add('hidden');
                if (reportSuccess) reportSuccess.classList.add('hidden');
                if (incorrectFeedback) incorrectFeedback.classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }
    }

    clearImageBtn.addEventListener('click', () => {
        fileInput.value = '';
        imagePreview.src = '';
        fileName.textContent = '';

        imagePreviewContent.classList.add('hidden');
        dropZoneContent.classList.remove('hidden');

        analyzeBtn.disabled = true;
        analyzeText.textContent = 'Select an image to analyze';

        const resultsSection = document.getElementById('resultsSection');
        const feedbackSuccess = document.getElementById('feedbackSuccess');
        const reportSuccess = document.getElementById('reportSuccess');
        const incorrectFeedback = document.getElementById('incorrectFeedback');

        if (resultsSection) resultsSection.classList.add('hidden');
        if (feedbackSuccess) feedbackSuccess.classList.add('hidden');
        if (reportSuccess) reportSuccess.classList.add('hidden');
        if (incorrectFeedback) incorrectFeedback.classList.add('hidden');

        dropZone.classList.remove('border-custom-primary');
    });

    const advancedToggle = document.getElementById('advancedToggle');
    const advancedSettings = document.getElementById('advancedSettings');
    const advancedArrow = document.getElementById('advancedArrow');

    if (advancedToggle && advancedSettings && advancedArrow) {
        advancedToggle.addEventListener('click', () => {
            advancedSettings.classList.toggle('hidden');
            advancedArrow.classList.toggle('rotate-180');
        });
    }

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

    const resultsSection = document.getElementById('resultsSection'); // Redeclared, ensure it's accessible

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

    const analysisModal = document.getElementById('analysisModal');
    const analysisModalContent = document.getElementById('analysisModalContent');
    const successModal = document.getElementById('successModal');
    const successModalContent = document.getElementById('successModalContent');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            if (analyzeBtn.disabled || !currentFile) return;

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

            try {
                const formData = new FormData();
                formData.append('screenshot', currentFile);
                formData.append('text_model', document.getElementById('textModel').value);
                formData.append('cnn_model', document.getElementById('cnnModel').value);
                formData.append('text_weight', textWeight.value);
                formData.append('cnn_weight', cnnWeight.value);

                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                clearInterval(stepInterval);

                if (!response.ok || !result.success) {
                    throw new Error(result.error || `Server error: ${response.status}`);
                }

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

                    showResults(result);
                }, 3000);

            } catch (error) {
                console.error('Analysis error:', error);

                clearInterval(stepInterval);

                hideModal(analysisModal, analysisModalContent);

                setTimeout(() => {
                    alert(`Analysis failed: ${error.message}`);

                    analyzeBtn.disabled = false;
                    analyzeText.textContent = 'Analyze Screenshot';
                }, 300);
            }
        });
    }

    const viewResultsBtn = document.getElementById('viewResultsBtn');

    if (viewResultsBtn && resultsSection) {
        viewResultsBtn.addEventListener('click', () => {
            hideModal(successModal, successModalContent);
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }, 300);
        });
    }

    function showResults(result) {
        const isScam = result.is_scam;
        const confidence = result.confidence;
        const textConf = result.text_confidence;
        const imageConf = result.image_confidence;
        const featureImportance = result.feature_importance || [];
        const extractedText = result.extracted_text || '';

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

        displayFeatureImportance(featureImportance, isScam);

        displayExtractedText(extractedText);

        resultsSection.classList.remove('hidden');
    }

    function displayFeatureImportance(featureImportance, isScam) {
        let featureContainer = document.getElementById('featureImportanceContainer');
        if (!featureContainer) {
            featureContainer = document.createElement('div');
            featureContainer.id = 'featureImportanceContainer';
            featureContainer.className = 'mt-6 p-4 rounded-lg border-2';

            const mainResult = document.getElementById('mainResult');
            if (mainResult) {
                mainResult.parentNode.insertBefore(featureContainer, mainResult.nextSibling);
            }
        }

        if (featureImportance && featureImportance.length > 0 && isScam) {
            featureContainer.className = 'mt-6 p-4 rounded-lg border-2 border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20';

            featureContainer.innerHTML = `
                <h3 class="text-lg font-semibold mb-3 text-red-600 dark:text-red-400 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    Detected Scam Indicators
                </h3>
                <div class="flex flex-wrap gap-2 mb-3">
                    ${featureImportance.map(feature => `
                        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border border-red-200 dark:border-red-700">
                            ${escapeHtml(feature.word)}
                            <span class="text-xs bg-red-200 dark:bg-red-800 px-1 rounded">
                                ${feature.importance.toFixed(3)}
                            </span>
                        </span>
                    `).join('')}
                </div>
                <p class="text-sm text-red-600 dark:text-red-400 italic">
                    These words/phrases contributed most to the scam detection based on your trained model. Higher scores indicate stronger scam indicators.
                </p>
            `;
        } else {
            featureContainer.style.display = 'none';
        }
    }

    function displayExtractedText(extractedText) {
        let textContainer = document.getElementById('extractedTextContainer');
        if (!textContainer) {
            textContainer = document.createElement('div');
            textContainer.id = 'extractedTextContainer';
            textContainer.className = 'mt-6 p-4 rounded-lg border-2 border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20';

            const featureContainer = document.getElementById('featureImportanceContainer');
            const insertAfter = featureContainer || document.getElementById('mainResult');
            if (insertAfter) {
                insertAfter.parentNode.insertBefore(textContainer, insertAfter.nextSibling);
            }
        }

        textContainer.innerHTML = `
            <h3 class="text-lg font-semibold mb-3 text-blue-600 dark:text-blue-400 flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Extracted Text
            </h3>
            <div class="bg-white dark:bg-gray-800 p-3 rounded border border-blue-200 dark:border-blue-700 max-h-48 overflow-y-auto">
                <pre class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">${escapeHtml(extractedText) || 'No text detected in the image.'}</pre>
            </div>
        `;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    const correctBtn = document.getElementById('correctBtn');
    const incorrectBtn = document.getElementById('incorrectBtn');
    const feedbackButtons = document.getElementById('feedbackButtons');
    const incorrectFeedback = document.getElementById('incorrectFeedback');
    const feedbackSuccess = document.getElementById('feedbackSuccess');
    const submitFeedback = document.getElementById('submitFeedback');

    if (correctBtn && feedbackButtons && feedbackSuccess) {
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
    }

    if (incorrectBtn && feedbackButtons && incorrectFeedback) {
        incorrectBtn.addEventListener('click', () => {
            feedbackButtons.classList.add('hidden');
            incorrectFeedback.classList.remove('hidden');
        });
    }

    if (submitFeedback && incorrectFeedback && feedbackSuccess) {
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
    }

    const reportScam = document.getElementById('reportScam');
    const reportSuccess = document.getElementById('reportSuccess');

    if (reportScam && reportSuccess) {
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
    }

    const carouselTrack = document.getElementById('carouselTrack');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carouselDotsContainer = document.getElementById('carouselDots');
    const carouselItems = document.querySelectorAll('.carousel-item');
    let currentSlide = 0;
    const totalSlides = carouselItems.length;

    const createCarouselDots = () => {
        if (!carouselDotsContainer) return;
        carouselDotsContainer.innerHTML = '';
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
        carouselTrack.style.transform = `translateX(${translateX}%)`;

        const dots = carouselDotsContainer.querySelectorAll('.carousel-dot');
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.remove('bg-gray-300', 'dark:bg-gray-600');
                dot.classList.add('bg-scam-primary');
            } else {
                dot.classList.remove('bg-scam-primary');
                dot.classList.add('bg-gray-300', 'dark:bg-gray-600');
            }
        });
    }

    createCarouselDots();
    updateCarousel();

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

    setInterval(() => {
        currentSlide = (currentSlide === totalSlides - 1) ? 0 : currentSlide + 1;
        updateCarousel();
    }, 5000);
});