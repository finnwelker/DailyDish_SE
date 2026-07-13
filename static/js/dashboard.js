const recipeExamplesSection = document.getElementById('recipe-examples-section');
const dashboardUserId = recipeExamplesSection ? recipeExamplesSection.dataset.userId : null;
const recipeExampleList = document.getElementById('recipe-example-list');
const loadDailyDishButton = document.getElementById('load-daily-dish-button');
const dailyDishResult = document.getElementById('daily-dish-result');
const dailyDishTitle = document.getElementById('daily-dish-title');
const dailyDishDescription = document.getElementById('daily-dish-description');
const dailyDishIngredients = document.getElementById('daily-dish-ingredients');
const dailyDishInstructions = document.getElementById('daily-dish-instructions');
const dailyDishTags = document.getElementById('daily-dish-tags');
const downloadDailyDishButton = document.getElementById('download-daily-dish-button');
const dashboardRecipeModal = document.getElementById('dashboard-recipe-modal');
const dashboardModalCloseButton = document.getElementById('dashboard-modal-close-button');
const dashboardModalTitle = document.getElementById('dashboard-modal-title');
const dashboardModalDescription = document.getElementById('dashboard-modal-description');
const dashboardModalIngredients = document.getElementById('dashboard-modal-ingredients');
const dashboardModalInstructions = document.getElementById('dashboard-modal-instructions');
const dashboardModalTags = document.getElementById('dashboard-modal-tags');
const dashboardModalAddFavouriteButton = document.getElementById('dashboard-modal-add-favourite-button');
const addToFavouritesButton = document.getElementById('add-to-favourites-button');
let currentDailyDishRecipe = null;
let displayedExampleRecipes = [];
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

    if (dashboardModalAddFavouriteButton && Number(dashboardModalAddFavouriteButton.dataset.recipeId) === normalizedRecipeId) {
        setFavouriteButtonState(dashboardModalAddFavouriteButton, isAdded);
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

    const actionRow = document.getElementById('daily-dish-action-row');
    if (actionRow) actionRow.style.display = 'flex';

    dailyDishTitle.textContent = recipe.title;
    dailyDishDescription.textContent = recipe.description;
    dailyDishIngredients.innerHTML = `<ul>${formatIngredientLines(recipe.ingredients)}</ul>`;
    dailyDishInstructions.innerHTML = formatInstructionSteps(recipe.instructions);
    dailyDishTags.innerHTML = (recipe.tags || [])
        .map(tag => `<span class="tag-pill">${escapeHtml(tag.name || tag)}</span>`)
        .join('');

    currentDailyDishRecipe = recipe;
    if (downloadDailyDishButton) {
        downloadDailyDishButton.disabled = false;
    }

    const addToFavouritesButton = document.getElementById('add-to-favourites-button');
    if (addToFavouritesButton && recipe.id) {
        addToFavouritesButton.dataset.recipeId = recipe.id;
        setFavouriteButtonState(addToFavouritesButton, favouriteRecipeIds.has(recipe.id));
        addToFavouritesButton.disabled = false;
    }
}

function renderRecipeExamples(recipes) {
    if (!recipeExampleList) return;

    if (!recipes.length) {
        recipeExampleList.innerHTML = '<p>Keine Rezept-Beispiele in der Datenbank gefunden.</p>';
        return;
    }

    recipeExampleList.innerHTML = recipes.map(recipe => {
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

function findDisplayedRecipeById(recipeId) {
    return displayedExampleRecipes.find(recipe => recipe.id === recipeId) || null;
}

function openDashboardRecipeModal(recipe) {
    if (!dashboardRecipeModal || !recipe) return;

    const tags = parseTags(recipe.tags);
    dashboardModalTitle.textContent = recipe.title || '';
    dashboardModalDescription.textContent = recipe.description || '';
    dashboardModalIngredients.innerHTML = `<ul>${formatIngredientLines(recipe.ingredients || '')}</ul>`;
    dashboardModalInstructions.innerHTML = formatInstructionSteps(recipe.instructions || '');
    dashboardModalTags.innerHTML = tags.map(tag => `<span class="tag-pill">${escapeHtml(tag)}</span>`).join('');

    if (dashboardModalAddFavouriteButton) {
        if (dashboardUserId) {
            dashboardModalAddFavouriteButton.disabled = false;
            dashboardModalAddFavouriteButton.dataset.recipeId = String(recipe.id);
            setFavouriteButtonState(dashboardModalAddFavouriteButton, favouriteRecipeIds.has(recipe.id));
        } else {
            dashboardModalAddFavouriteButton.disabled = true;
            dashboardModalAddFavouriteButton.removeAttribute('data-recipe-id');
            dashboardModalAddFavouriteButton.innerHTML = '<span class="btn-icon">&#x21AA;</span>Bitte einloggen';
        }
    }

    dashboardRecipeModal.classList.remove('hidden');
    dashboardRecipeModal.style.display = 'flex';
}

function closeDashboardRecipeModal() {
    if (!dashboardRecipeModal) return;
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

        const allRecipes = await response.json();
        displayedExampleRecipes = pickRandomRecipes(allRecipes || [], 2);
        renderRecipeExamples(displayedExampleRecipes);
    } catch (error) {
        console.error(error);
        recipeExampleList.innerHTML = '<p>Rezept-Beispiele konnten nicht geladen werden.</p>';
    }
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
    loadDailyDishButton.addEventListener('click', async () => {
        const userId = loadDailyDishButton.dataset.userId;

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

if (recipeExampleList) {
    recipeExampleList.addEventListener('click', async event => {
        const favouriteButton = event.target.closest('.example-add-favourite-button');
        if (favouriteButton) {
            const recipeId = Number(favouriteButton.dataset.recipeId);
            if (!recipeId) return;
            await toggleRecipeFavourite(recipeId, favouriteButton.dataset.added === 'true');
            return;
        }

        const card = event.target.closest('.example-recipe-card');
        if (!card) return;
        const recipeId = Number(card.dataset.recipeId);
        if (!recipeId) return;
        openDashboardRecipeModal(findDisplayedRecipeById(recipeId));
    });

    recipeExampleList.addEventListener('keydown', event => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        const card = event.target.closest('.example-recipe-card');
        if (!card) return;
        event.preventDefault();
        const recipeId = Number(card.dataset.recipeId);
        if (!recipeId) return;
        openDashboardRecipeModal(findDisplayedRecipeById(recipeId));
    });

    recipeExampleList.addEventListener('error', event => {
        const image = event.target;
        if (!(image instanceof HTMLImageElement) || !image.classList.contains('example-recipe-image')) return;
        const wrapper = image.closest('.example-recipe-image-wrap');
        if (wrapper) wrapper.classList.add('image-failed');
    }, true);
}

if (dashboardModalAddFavouriteButton) {
    dashboardModalAddFavouriteButton.classList.add('favourite-toggle-button');
    dashboardModalAddFavouriteButton.addEventListener('click', async () => {
        const recipeId = Number(dashboardModalAddFavouriteButton.dataset.recipeId || '0');
        if (!recipeId) return;
        await toggleRecipeFavourite(recipeId, dashboardModalAddFavouriteButton.dataset.added === 'true');
    });

    dashboardModalAddFavouriteButton.addEventListener('mouseenter', () => setFavouriteButtonHoverState(dashboardModalAddFavouriteButton, true));
    dashboardModalAddFavouriteButton.addEventListener('mouseleave', () => setFavouriteButtonHoverState(dashboardModalAddFavouriteButton, false));
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

if (recipeExampleList) {
    recipeExampleList.addEventListener('mouseover', event => {
        const button = event.target.closest('.example-add-favourite-button');
        if (!button) return;
        setFavouriteButtonHoverState(button, true);
    });

    recipeExampleList.addEventListener('mouseout', event => {
        const button = event.target.closest('.example-add-favourite-button');
        if (!button) return;
        setFavouriteButtonHoverState(button, false);
    });
}
