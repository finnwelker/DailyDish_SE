const dashboardContentStack = document.getElementById('dashboard-content-stack');
const dashboardUserId = dashboardContentStack ? dashboardContentStack.dataset.userId : null;
const recipeExampleList = document.getElementById('recipe-example-list');
const recipeSearchInput = document.getElementById('recipe-search-input');
const recipeSearchResultList = document.getElementById('recipe-search-result-list');
const recipeSearchFieldWrap = document.querySelector('.recipe-search-field-wrap');
const loadDailyDishButton = document.getElementById('load-daily-dish-button');
const dailyDishCta = document.querySelector('.daily-dish-cta');
const dailyDishCtaNote = document.querySelector('.daily-dish-cta-note');
const dailyDishResult = document.getElementById('daily-dish-result');
const dailyDishTitle = document.getElementById('daily-dish-title');
const dailyDishDescription = document.getElementById('daily-dish-description');
const dailyDishImage = document.getElementById('daily-dish-image');
const dailyDishIngredients = document.getElementById('daily-dish-ingredients');
const dailyDishInstructions = document.getElementById('daily-dish-instructions');
const dailyDishTags = document.getElementById('daily-dish-tags');
const downloadDailyDishButton = document.getElementById('download-daily-dish-button');
const loadNextRecipeButton = document.getElementById('load-next-recipe-button');
const dashboardRecipeModal = document.getElementById('dashboard-recipe-modal');
const dashboardModalCloseButton = document.getElementById('dashboard-modal-close-button');
const dashboardModalTitle = document.getElementById('dashboard-modal-title');
const dashboardModalDescription = document.getElementById('dashboard-modal-description');
const dashboardModalIngredients = document.getElementById('dashboard-modal-ingredients');
const dashboardModalInstructions = document.getElementById('dashboard-modal-instructions');
const dashboardModalTags = document.getElementById('dashboard-modal-tags');
const dashboardModalDownloadButton = document.getElementById('dashboard-modal-download-button');
const addToFavouritesButton = document.getElementById('add-to-favourites-button');
let currentDailyDishRecipe = null;
let currentDashboardModalRecipe = null;
let allDashboardRecipes = [];
let recipesById = new Map();
let favouriteRecipeIds = new Set();

const favouriteButtonLabels = {
    add: '<span class="btn-icon">&#x2661;</span>Zu Favoriten hinzufügen',
    saved: '<span class="btn-icon">&#x2665;</span>In Favoriten gespeichert',
    remove: '<span class="btn-icon">&#x2665;</span>Aus Favoriten entfernen'
};

function formatIngredientLines(ingredientsText) {
    return ingredientsText
        .split(',')
        .map(item => item.trim())
        .filter(Boolean)
        .map(item => `<li class="ingredient-line">${item}</li>`)
        .join('');
}

function formatInstructionSteps(instructionsText) {
    return instructionsText
        .split(/(?=\d+\.)/)
        .map(step => step.trim())
        .filter(Boolean)
        .map(step => `<p class="instruction-step">${step}</p>`)
        .join('');
}

function escapeHtml(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function parseTags(tags) {
    return (tags || [])
        .map(tag => (typeof tag === 'string' ? tag : tag && tag.name))
        .filter(Boolean);
}

function pickRandomRecipes(recipes, count) {
    const shuffled = [...recipes];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled.slice(0, count);
}

function setFavouriteButtonState(button, isAdded) {
    if (!button) return;
    button.dataset.added = isAdded ? 'true' : 'false';
    button.innerHTML = isAdded ? favouriteButtonLabels.saved : favouriteButtonLabels.add;
}

function setFavouriteButtonHoverState(button, isHovering) {
    if (!button) return;
    if (button.dataset.added !== 'true') return;
    button.innerHTML = isHovering ? favouriteButtonLabels.remove : favouriteButtonLabels.saved;
}

function updateFavouriteButtonsForRecipe(recipeId, isAdded) {
    const normalizedRecipeId = Number(recipeId);
    if (!normalizedRecipeId) return;

    if (isAdded) {
        favouriteRecipeIds.add(normalizedRecipeId);
    } else {
        favouriteRecipeIds.delete(normalizedRecipeId);
    }

    if (addToFavouritesButton && Number(addToFavouritesButton.dataset.recipeId) === normalizedRecipeId) {
        setFavouriteButtonState(addToFavouritesButton, isAdded);
    }

    const buttons = document.querySelectorAll(`.example-add-favourite-button[data-recipe-id="${normalizedRecipeId}"]`);
    buttons.forEach(button => setFavouriteButtonState(button, isAdded));
}

async function toggleRecipeFavourite(recipeId, isCurrentlyAdded) {
    if (!dashboardUserId || !recipeId) return;

    const method = isCurrentlyAdded ? 'DELETE' : 'POST';
    try {
        const response = await fetch(`/user/${dashboardUserId}/favourites/${recipeId}`, { method });
        if (response.ok || response.status === 400) {
            updateFavouriteButtonsForRecipe(recipeId, !isCurrentlyAdded);
        }
    } catch (error) {
        console.error('Fehler beim Aktualisieren der Favoriten:', error);
    }
}

function renderDailyDish(recipe) {
    if (!dailyDishResult || !dailyDishTitle || !dailyDishDescription || !dailyDishIngredients || !dailyDishInstructions || !dailyDishTags) return;

    dailyDishResult.classList.remove('hidden');
    // Retrigger reveal animation each time a new suggestion is rendered.
    dailyDishResult.classList.remove('daily-dish-result-reveal');
    // Force reflow so the class re-add starts animation from frame 0.
    void dailyDishResult.offsetWidth;
    dailyDishResult.classList.add('daily-dish-result-reveal');

    const actionRow = document.getElementById('daily-dish-action-row');
    if (actionRow) actionRow.style.display = 'flex';

    dailyDishTitle.textContent = recipe.title;
    dailyDishDescription.textContent = recipe.description;
    if (dailyDishImage) {
        dailyDishImage.src = `/static/images/recipes/${recipe.id}.jpg`;
        dailyDishImage.alt = recipe.title || 'Rezeptbild';
        dailyDishImage.classList.remove('image-failed');
    }
    dailyDishIngredients.innerHTML = `<ul>${formatIngredientLines(recipe.ingredients)}</ul>`;
    dailyDishInstructions.innerHTML = formatInstructionSteps(recipe.instructions);
    dailyDishTags.innerHTML = (recipe.tags || [])
        .map(tag => `<span class="tag-pill">${escapeHtml(tag.name || tag)}</span>`)
        .join('');

    currentDailyDishRecipe = recipe;
    if (downloadDailyDishButton) {
        downloadDailyDishButton.disabled = false;
    }
    if (loadNextRecipeButton) {
        loadNextRecipeButton.disabled = false;
    }

    const addToFavouritesButton = document.getElementById('add-to-favourites-button');
    if (addToFavouritesButton && recipe.id) {
        addToFavouritesButton.dataset.recipeId = recipe.id;
        setFavouriteButtonState(addToFavouritesButton, favouriteRecipeIds.has(recipe.id));
        addToFavouritesButton.disabled = false;
    }
}

function renderRecipeCards(listElement, recipes, emptyMessage) {
    if (!listElement) return;

    if (!recipes.length) {
        listElement.innerHTML = `<p>${escapeHtml(emptyMessage)}</p>`;
        return;
    }

    listElement.innerHTML = recipes.map(recipe => {
        const tags = parseTags(recipe.tags);
        const isFavourite = favouriteRecipeIds.has(recipe.id);
        const addButtonHtml = dashboardUserId
            ? `<button class="button dashboard-edit-tags-button favourite-toggle-button example-add-favourite-button" type="button" data-action="add-favourite" data-recipe-id="${recipe.id}" data-added="${isFavourite ? 'true' : 'false'}">${isFavourite ? favouriteButtonLabels.saved : favouriteButtonLabels.add}</button>`
            : '<a class="button dashboard-edit-tags-button" href="/login"><span class="btn-icon">&#x21AA;</span>Login für Favoriten</a>';

        return `
            <article class="example-recipe-card" data-recipe-id="${recipe.id}" role="button" tabindex="0" aria-label="${escapeHtml(recipe.title)} anzeigen">
                <div class="example-recipe-image-wrap">
                    <img class="example-recipe-image" src="/static/images/recipes/${recipe.id}.jpg" alt="${escapeHtml(recipe.title)}" loading="lazy">
                    <span class="example-recipe-placeholder" aria-hidden="true">&#x1F37D;&#xFE0F;</span>
                </div>
                <div class="example-recipe-content">
                    <h4>${escapeHtml(recipe.title)}</h4>
                    <p>${escapeHtml(recipe.description || '')}</p>
                    <div class="tag-pill-list">
                        ${tags.map(tag => `<span class="tag-pill">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                    <div class="example-recipe-actions">
                        ${addButtonHtml}
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

async function loadFavouriteRecipeIds() {
    if (!dashboardUserId) return;

    try {
        const response = await fetch(`/user/${dashboardUserId}/favourites`);
        if (!response.ok) return;
        const favourites = await response.json();
        favouriteRecipeIds = new Set((favourites || []).map(recipe => recipe.id));
    } catch (error) {
        console.error('Fehler beim Laden der Favoriten:', error);
    }
}

function openDashboardRecipeModal(recipe) {
    if (!dashboardRecipeModal || !recipe) return;

    const tags = parseTags(recipe.tags);
    dashboardModalTitle.textContent = recipe.title || '';
    dashboardModalDescription.textContent = recipe.description || '';
    dashboardModalIngredients.innerHTML = `<ul>${formatIngredientLines(recipe.ingredients || '')}</ul>`;
    dashboardModalInstructions.innerHTML = formatInstructionSteps(recipe.instructions || '');
    dashboardModalTags.innerHTML = tags.map(tag => `<span class="tag-pill">${escapeHtml(tag)}</span>`).join('');

    currentDashboardModalRecipe = {
        title: recipe.title || '',
        description: recipe.description || '',
        ingredients: recipe.ingredients || '',
        instructions: recipe.instructions || '',
        tags: tags
    };

    if (dashboardModalDownloadButton) {
        dashboardModalDownloadButton.disabled = false;
    }

    dashboardRecipeModal.classList.remove('hidden');
    dashboardRecipeModal.style.display = 'flex';
}

function closeDashboardRecipeModal() {
    if (!dashboardRecipeModal) return;
    currentDashboardModalRecipe = null;

    if (dashboardModalDownloadButton) {
        dashboardModalDownloadButton.disabled = true;
    }

    dashboardRecipeModal.classList.add('hidden');
    dashboardRecipeModal.style.display = '';
}

async function loadRecipeExamplesFromDatabase() {
    if (!recipeExampleList) return;

    try {
        const response = await fetch('/recipes');
        if (!response.ok) {
            throw new Error('Rezeptliste konnte nicht geladen werden');
        }

        allDashboardRecipes = await response.json();
        recipesById = new Map((allDashboardRecipes || []).map(recipe => [recipe.id, recipe]));

        const randomExamples = pickRandomRecipes(allDashboardRecipes || [], 2);
        renderRecipeCards(recipeExampleList, randomExamples, 'Keine Rezept-Beispiele in der Datenbank gefunden.');

        if (recipeSearchResultList) {
            recipeSearchResultList.innerHTML = '';
        }
    } catch (error) {
        console.error(error);
        recipeExampleList.innerHTML = '<p>Rezept-Beispiele konnten nicht geladen werden.</p>';
    }
}

function searchRecipes(query) {
    const normalizedQuery = String(query || '').trim().toLowerCase();
    if (!normalizedQuery) {
        return [];
    }

    const terms = normalizedQuery.split(/\s+/).filter(Boolean);
    return (allDashboardRecipes || []).filter(recipe => {
        const title = String(recipe.title || '').toLowerCase();
        const tags = parseTags(recipe.tags).join(' ').toLowerCase();
        const haystack = `${title} ${tags}`;
        return terms.every(term => haystack.includes(term));
    });
}

function openSearchResults() {
    if (!recipeSearchFieldWrap || !recipeSearchResultList) return;
    if (!recipeSearchResultList.innerHTML.trim()) return;
    recipeSearchFieldWrap.classList.add('search-results-open');
}

function closeSearchResults() {
    if (!recipeSearchFieldWrap) return;
    recipeSearchFieldWrap.classList.remove('search-results-open');
}

function attachRecipeListInteractions(listElement) {
    if (!listElement) return;

    listElement.addEventListener('click', async event => {
        const favouriteButton = event.target.closest('.example-add-favourite-button');
        if (favouriteButton) {
            const recipeId = Number(favouriteButton.dataset.recipeId);
            if (!recipeId) return;
            await toggleRecipeFavourite(recipeId, favouriteButton.dataset.added === 'true');
            return;
        }

        // Tag-pill clicks should only trigger tag actions, not open the recipe modal.
        if (event.target.closest('.tag-pill')) {
            return;
        }

        const card = event.target.closest('.example-recipe-card');
        if (!card) return;
        const recipeId = Number(card.dataset.recipeId);
        if (!recipeId) return;
        openDashboardRecipeModal(recipesById.get(recipeId) || null);
    });

    listElement.addEventListener('keydown', event => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        const card = event.target.closest('.example-recipe-card');
        if (!card) return;
        event.preventDefault();
        const recipeId = Number(card.dataset.recipeId);
        if (!recipeId) return;
        openDashboardRecipeModal(recipesById.get(recipeId) || null);
    });

    listElement.addEventListener('error', event => {
        const image = event.target;
        if (!(image instanceof HTMLImageElement) || !image.classList.contains('example-recipe-image')) return;
        const wrapper = image.closest('.example-recipe-image-wrap');
        if (wrapper) wrapper.classList.add('image-failed');
    }, true);

    listElement.addEventListener('mouseover', event => {
        const button = event.target.closest('.example-add-favourite-button');
        if (!button) return;
        setFavouriteButtonHoverState(button, true);
    });

    listElement.addEventListener('mouseout', event => {
        const button = event.target.closest('.example-add-favourite-button');
        if (!button) return;
        setFavouriteButtonHoverState(button, false);
    });
}

if (downloadDailyDishButton) {
    downloadDailyDishButton.addEventListener('click', () => {
        if (!currentDailyDishRecipe || typeof window.downloadRecipeAsPdf !== 'function') return;
        window.downloadRecipeAsPdf({
            title: currentDailyDishRecipe.title,
            description: currentDailyDishRecipe.description,
            ingredients: currentDailyDishRecipe.ingredients,
            instructions: currentDailyDishRecipe.instructions,
            tags: (currentDailyDishRecipe.tags || []).map(tag => tag.name || tag)
        });
    });
}

if (loadDailyDishButton && dailyDishResult) {
    if (dailyDishImage) {
        dailyDishImage.addEventListener('error', () => {
            dailyDishImage.classList.add('image-failed');
        });
    }

    loadDailyDishButton.addEventListener('click', async () => {
        const userId = loadDailyDishButton.dataset.userId;

        if (dailyDishCtaNote) {
            dailyDishCtaNote.classList.add('hidden');
        }
        if (dailyDishCta) {
            dailyDishCta.classList.add('daily-dish-cta-collapsed');
        }

        if (!userId) {
            dailyDishTitle.textContent = 'Bitte logge dich ein';
            dailyDishDescription.textContent = 'Der Daily Dish-Vorschlag steht nur für angemeldete Nutzer zur Verfügung.';
            dailyDishIngredients.innerHTML = '';
            dailyDishInstructions.innerHTML = '';
            dailyDishTags.innerHTML = '';
            dailyDishResult.classList.remove('hidden');
            loadDailyDishButton.classList.add('hidden');
            return;
        }

        try {
            const response = await fetch(`/suggestions/${userId}`);
            if (!response.ok) {
                throw new Error('Keine passende Empfehlung gefunden');
            }

            const recipe = await response.json();
            renderDailyDish(recipe);
            loadDailyDishButton.classList.add('hidden');
        } catch (error) {
            dailyDishTitle.textContent = 'Kein passender Vorschlag';
            dailyDishDescription.textContent = 'Für deinen aktuellen Tag-Stand gibt es noch keinen passenden Vorschlag.';
            dailyDishIngredients.innerHTML = '';
            dailyDishInstructions.innerHTML = '';
            dailyDishTags.innerHTML = '';
            dailyDishResult.classList.remove('hidden');
            loadDailyDishButton.classList.add('hidden');
        }
    });
}

if (loadNextRecipeButton && loadDailyDishButton) {
    loadNextRecipeButton.addEventListener('click', async () => {
        const userId = loadDailyDishButton.dataset.userId;
        if (!userId) return;

        try {
            const response = await fetch(`/suggestions/${userId}?skip=true`);
            if (!response.ok) {
                throw new Error('Kein weiterer Vorschlag gefunden');
            }

            const recipe = await response.json();
            renderDailyDish(recipe);
            loadDailyDishButton.classList.add('hidden');
        } catch (error) {
            console.error(error);
        }
    });
}

attachRecipeListInteractions(recipeExampleList);
attachRecipeListInteractions(recipeSearchResultList);

if (dashboardModalDownloadButton) {
    dashboardModalDownloadButton.addEventListener('click', () => {
        if (!currentDashboardModalRecipe || typeof window.downloadRecipeAsPdf !== 'function') return;
        window.downloadRecipeAsPdf(currentDashboardModalRecipe);
    });
}

if (dashboardRecipeModal) {
    dashboardRecipeModal.addEventListener('click', event => {
        if (event.target === dashboardRecipeModal) {
            closeDashboardRecipeModal();
        }
    });
}

if (dashboardModalCloseButton) {
    dashboardModalCloseButton.addEventListener('click', closeDashboardRecipeModal);
}

(async function initRecipeExamples() {
    await loadFavouriteRecipeIds();
    await loadRecipeExamplesFromDatabase();
})();

if (recipeSearchInput && recipeSearchResultList) {
    recipeSearchInput.addEventListener('input', () => {
        const query = recipeSearchInput.value;
        const matches = searchRecipes(query);

        if (!query.trim()) {
            recipeSearchResultList.innerHTML = '';
            closeSearchResults();
            return;
        }

        renderRecipeCards(recipeSearchResultList, matches, 'Keine passenden Rezepte gefunden.');
        openSearchResults();
    });

    recipeSearchInput.addEventListener('focus', () => {
        if (recipeSearchInput.value.trim()) {
            openSearchResults();
        }
    });

    recipeSearchInput.addEventListener('click', () => {
        if (recipeSearchInput.value.trim()) {
            openSearchResults();
        }
    });

    document.addEventListener('click', event => {
        if (!recipeSearchFieldWrap) return;
        if (recipeSearchFieldWrap.contains(event.target)) return;
        closeSearchResults();
    });
}

if (addToFavouritesButton && loadDailyDishButton) {
    addToFavouritesButton.classList.add('favourite-toggle-button');
    // Hover behavior: show "Aus Favoriten entfernen" on hover if added
    addToFavouritesButton.addEventListener('mouseenter', () => {
        setFavouriteButtonHoverState(addToFavouritesButton, true);
    });

    addToFavouritesButton.addEventListener('mouseleave', () => {
        setFavouriteButtonHoverState(addToFavouritesButton, false);
    });

    addToFavouritesButton.addEventListener('click', async () => {
        const userId = loadDailyDishButton.dataset.userId;
        const recipeId = addToFavouritesButton.dataset.recipeId;
        if (!userId || !recipeId) return;

        await toggleRecipeFavourite(Number(recipeId), addToFavouritesButton.dataset.added === 'true');
    });
}

