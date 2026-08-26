document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('promptInput');
    const generateBtn = document.getElementById('generateBtn');
    const imageGrid = document.getElementById('imageGrid');
    const placeholderText = document.getElementById('placeholderText');
    const scrollToGeneratorBtn = document.getElementById('scrollToGenerator');
    const imageGeneratorSection = document.getElementById('image-generator');
    const ratioButtons = document.querySelectorAll('.ratio-btn');
    const stylePreset = document.getElementById('stylePreset');
    const exampleTags = document.querySelectorAll('.example-tag');

    // Smooth Scroll to Generator
    if (scrollToGeneratorBtn) {
        scrollToGeneratorBtn.addEventListener('click', () => {
            imageGeneratorSection.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Example Tags
    exampleTags.forEach(tag => {
        tag.addEventListener('click', () => {
            promptInput.value = tag.innerText;
            promptInput.focus();
        });
    });

    // Ratio Selection
    let selectedRatio = '1:1';
    ratioButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            ratioButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedRatio = btn.dataset.ratio;
        });
    });

    // Style Mappings
    const styleKeywords = {
        'realistic': 'photorealistic, 8k, highly detailed, sharp focus, masterpiece',
        'anime': 'anime style, digital art, vibrant colors, clean lines, studio ghibli inspired',
        'cinematic': 'cinematic lighting, dramatic shadows, movie still, wide angle, moody',
        'illustration': 'digital illustration, hand drawn style, artistic, creative, vector art',
        'logo': 'minimalist logo, vector, flat design, clean lines, white background, professional'
    };

    generateBtn.addEventListener('click', async () => {
        const basePrompt = promptInput.value.trim();
        const selectedStyle = stylePreset.value;

        if (!basePrompt) {
            alert("Please enter a description for your image.");
            return;
        }

        // Hide placeholder on first generation
        if (placeholderText) placeholderText.style.display = 'none';

        // Prepare full prompt
        let fullPrompt = basePrompt;
        if (selectedStyle && styleKeywords[selectedStyle]) {
            fullPrompt += `, ${styleKeywords[selectedStyle]}`;
        }

        // Add ratio hints to prompt (as we can't touch backend)
        if (selectedRatio !== '1:1') {
            fullPrompt += `, ${selectedRatio} aspect ratio`;
        }

        // Create Skeleton Item
        const skeletonItem = createSkeletonItem(selectedRatio);
        imageGrid.prepend(skeletonItem);

        // Disable UI
        setLoading(true);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: fullPrompt })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate image');
            }

            if (data.image) {
                // Success: Replace skeleton with real image
                const imageItem = createImageItem(data.image, basePrompt, selectedRatio);
                imageGrid.replaceChild(imageItem, skeletonItem);
            } else {
                throw new Error('No image data received');
            }

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            skeletonItem.remove(); // Remove skeleton on error
            if (imageGrid.children.length === 0) {
                placeholderText.style.display = 'flex';
            }
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        generateBtn.innerHTML = isLoading ?
            '<span class="loading-spinner-small"></span> Generating...' :
            '✨ Generate Masterpiece';
        promptInput.disabled = isLoading;
    }

    function createSkeletonItem(ratio) {
        const item = document.createElement('div');
        item.className = 'image-item skeleton-item';

        const ratioClass = ratio === '16:9' ? 'ratio-16-9' : (ratio === '9:16' ? 'ratio-9-16' : '');

        item.innerHTML = `
            <div class="image-wrapper ${ratioClass} skeleton"></div>
            <div class="image-info">
                <div class="skeleton" style="height: 14px; width: 60%; border-radius: 4px;"></div>
                <div class="skeleton" style="height: 36px; width: 36px; border-radius: 10px;"></div>
            </div>
        `;
        return item;
    }

    function createImageItem(base64Image, prompt, ratio) {
        const item = document.createElement('div');
        item.className = 'image-item';

        const ratioClass = ratio === '16:9' ? 'ratio-16-9' : (ratio === '9:16' ? 'ratio-9-16' : '');
        const timestamp = new Date().getTime();
        const filename = `ai-art-${timestamp}.png`;

        item.innerHTML = `
            <div class="image-wrapper ${ratioClass}">
                <img src="${base64Image}" alt="${prompt}" loading="lazy">
            </div>
            <div class="image-info">
                <p title="${prompt}">${prompt}</p>
                <a href="${base64Image}" download="${filename}" class="download-icon-btn" title="Download Image">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                </a>
            </div>
        `;
        return item;
    }
});

