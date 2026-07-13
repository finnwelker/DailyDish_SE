function formatIngredientLines(text) {
    return text.split(',').map(i => i.trim()).filter(Boolean)
        .map(i => `<li class="ingredient-line">${i}</li>`).join('');
}

function formatInstructionSteps(text) {
    return text.split(/(?=\d+\.)/).map(s => s.trim()).filter(Boolean)
        .map(s => `<p class="instruction-step">${s}</p>`).join('');
}

function openRecipeModal(cardEl) {
    const modal = document.getElementById('recipe-modal');
    const tags = (cardEl.dataset.tags || '').split(',').map(t => t.trim()).filter(Boolean);
    document.getElementById('modal-title').textContent = cardEl.dataset.title || '';
    document.getElementById('modal-description').textContent = cardEl.dataset.description || '';
    document.getElementById('modal-ingredients').innerHTML =
        '<ul>' + formatIngredientLines(cardEl.dataset.ingredients || '') + '</ul>';
    document.getElementById('modal-instructions').innerHTML =
        formatInstructionSteps(cardEl.dataset.instructions || '');
    document.getElementById('modal-tags').innerHTML =
        tags
            .map(t => `<span class="tag-pill">${t}</span>`).join('');

    window.currentModalRecipe = {
        title: cardEl.dataset.title || '',
        description: cardEl.dataset.description || '',
        ingredients: cardEl.dataset.ingredients || '',
        instructions: cardEl.dataset.instructions || '',
        tags: tags
    };

    const downloadButton = document.getElementById('download-modal-recipe-button');
    if (downloadButton) {
        downloadButton.disabled = false;
    }

    modal.classList.remove('hidden');
    modal.style.display = 'flex';
}

function closeRecipeModal() {
    const modal = document.getElementById('recipe-modal');
    window.currentModalRecipe = null;

    const downloadButton = document.getElementById('download-modal-recipe-button');
    if (downloadButton) {
        downloadButton.disabled = true;
    }

    modal.classList.add('hidden');
    modal.style.display = '';
}

const downloadModalRecipeButton = document.getElementById('download-modal-recipe-button');
if (downloadModalRecipeButton) {
    downloadModalRecipeButton.addEventListener('click', () => {
        if (window.currentModalRecipe && typeof window.downloadRecipeAsPdf === 'function') {
            window.downloadRecipeAsPdf(window.currentModalRecipe);
        }
    });
}

async function removeFavourite(button) {
    const recipeId = button.dataset.recipeId;
    const pageEl = document.getElementById('favourites-page');
    const userId = pageEl ? pageEl.dataset.userId : null;
    if (!userId || !recipeId) return;
    try {
        const response = await fetch(`/user/${userId}/favourites/${recipeId}`, { method: 'DELETE' });
        if (response.ok) {
            const card = document.getElementById(`fav-card-${recipeId}`);
            if (card) {
                card.style.transition = 'opacity 0.3s ease';
                card.style.opacity = '0';
                setTimeout(() => card.remove(), 300);
            }
        }
    } catch (e) {
        console.error(e);
    }
}
