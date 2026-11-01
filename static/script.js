document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generatorForm');
    const promptInput = document.getElementById('promptInput');
    const generateBtn = document.getElementById('generateBtn');
    const imageGrid = document.getElementById('imageGrid');
    const placeholderText = document.getElementById('placeholderText');
    const outputArea = document.getElementById('outputArea');
    const errorMessage = document.getElementById('generationError');
    const promptCounter = document.getElementById('promptCounter');
    const galleryCount = document.getElementById('galleryCount');
    const ratioButtons = document.querySelectorAll('.ratio-btn');
    const stylePreset = document.getElementById('stylePreset');
    const exampleButtons = document.querySelectorAll('.example-chip');

    if (!form || !promptInput || !generateBtn || !imageGrid) return;

    const styleKeywords = {
        realistic: 'photorealistic, natural lighting, finely detailed',
        illustration: 'editorial illustration, considered color palette, refined composition',
        cinematic: 'cinematic composition, atmospheric lighting, film still',
        anime: 'anime illustration, expressive details, hand-painted background',
        logo: 'clean graphic design, minimal vector shapes, balanced composition'
    };

    let selectedRatio = '1:1';

    const updatePromptCount = () => {
        promptCounter.textContent = promptInput.value.length.toLocaleString() + ' / 2,048';
    };

    promptInput.addEventListener('input', updatePromptCount);

    exampleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            promptInput.value = button.dataset.prompt || button.textContent.trim();
            updatePromptCount();
            promptInput.focus();
        });
    });

    ratioButtons.forEach((button) => {
        button.addEventListener('click', () => {
            ratioButtons.forEach((item) => {
                item.classList.remove('active');
                item.setAttribute('aria-pressed', 'false');
            });
            button.classList.add('active');
            button.setAttribute('aria-pressed', 'true');
            selectedRatio = button.dataset.ratio || '1:1';
        });
    });

    promptInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const basePrompt = promptInput.value.trim();
        if (!basePrompt) {
            promptInput.focus();
            promptInput.setAttribute('aria-invalid', 'true');
            showError('Add a description of the image you want to create.');
            return;
        }
        promptInput.removeAttribute('aria-invalid');
        hideError();

        const selectedStyle = stylePreset.value;
        let fullPrompt = basePrompt;
        if (selectedStyle && styleKeywords[selectedStyle]) {
            fullPrompt += ', ' + styleKeywords[selectedStyle];
        }

        const skeletonItem = createSkeletonItem(selectedRatio);
        imageGrid.prepend(skeletonItem);
        if (placeholderText) placeholderText.hidden = true;
        outputArea.setAttribute('aria-busy', 'true');
        setLoading(true);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: fullPrompt, ratio: selectedRatio })
            });
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.error || 'We could not create the image. Please try again.');
            }
            if (!data.image) {
                throw new Error('The image service returned an empty result. Please try again.');
            }

            const imageItem = createImageItem(data.image, basePrompt, selectedRatio);
            imageGrid.replaceChild(imageItem, skeletonItem);
            updateGalleryCount();
        } catch (error) {
            skeletonItem.remove();
            showError(error.message || 'Something went wrong. Please try again.');
            if (imageGrid.children.length === 0 && placeholderText) {
                placeholderText.hidden = false;
            }
        } finally {
            outputArea.setAttribute('aria-busy', 'false');
            setLoading(false);
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.hidden = false;
    }

    function hideError() {
        errorMessage.hidden = true;
        errorMessage.textContent = '';
    }

    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        generateBtn.setAttribute('aria-busy', String(isLoading));
        generateBtn.innerHTML = isLoading
            ? '<span class="loading-spinner" aria-hidden="true"></span><span>Creating your image…</span>'
            : '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><path d="M12 3v18M3 12h18M5.64 5.64l12.72 12.72m0-12.72L5.64 18.36" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg><span>Generate image</span><span class="button-arrow" aria-hidden="true">↗</span>';
        promptInput.disabled = isLoading;
        stylePreset.disabled = isLoading;
        ratioButtons.forEach((button) => { button.disabled = isLoading; });
        exampleButtons.forEach((button) => { button.disabled = isLoading; });
    }

    function createSkeletonItem(ratio) {
        const item = document.createElement('article');
        item.className = 'image-item skeleton-item';
        item.setAttribute('aria-label', 'Generating image');
        const image = document.createElement('div');
        image.className = 'image-wrapper ' + getRatioClass(ratio) + ' skeleton';
        const caption = document.createElement('div');
        caption.className = 'image-info skeleton-caption';
        const line = document.createElement('span');
        line.className = 'skeleton-line';
        line.setAttribute('aria-hidden', 'true');
        caption.appendChild(line);
        item.append(image, caption);
        return item;
    }

    function createImageItem(imageUrl, prompt, ratio) {
        const item = document.createElement('article');
        item.className = 'image-item';

        const wrapper = document.createElement('div');
        wrapper.className = 'image-wrapper ' + getRatioClass(ratio);
        const image = document.createElement('img');
        image.src = imageUrl;
        image.alt = prompt;
        image.loading = 'lazy';
        wrapper.appendChild(image);

        const info = document.createElement('div');
        info.className = 'image-info';
        const caption = document.createElement('p');
        caption.textContent = prompt;
        caption.title = prompt;
        const download = document.createElement('a');
        download.href = imageUrl;
        download.download = 'ayman-image-' + Date.now() + '.jpg';
        download.className = 'download-btn';
        download.setAttribute('aria-label', 'Download generated image');
        download.title = 'Download image';
        download.innerHTML = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 3v11m0 0 4-4m-4 4-4-4M5 15v4a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        info.append(caption, download);
        item.append(wrapper, info);
        return item;
    }

    function getRatioClass(ratio) {
        if (ratio === '16:9') return 'ratio-16-9';
        if (ratio === '9:16') return 'ratio-9-16';
        return '';
    }

    function updateGalleryCount() {
        const count = imageGrid.querySelectorAll('.image-item:not(.skeleton-item)').length;
        galleryCount.textContent = count ? '(' + count + ')' : '';
    }
});
