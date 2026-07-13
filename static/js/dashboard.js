const sampleRecipes = [
    {
        title: 'Sommer-Pasta',
        description: 'Ein schnelles Pastagericht mit Tomaten, Knoblauch und frischem Basilikum.',
        ingredients: ['Pasta', 'Tomaten', 'Knoblauch', 'Olivenöl', 'Basilikum'],
        duration: '20 Minuten',
        tags: ['schnell', 'frisch', 'vegetarisch']
    },
    {
        title: 'Ofenkartoffeln mit Kräuterquark',
        description: 'Goldbraune Kartoffeln aus dem Ofen mit cremigem Kräuterquark.',
        ingredients: ['Kartoffeln', 'Quark', 'Schnittlauch', 'Petersilie', 'Zitrone'],
        duration: '35 Minuten',
        tags: ['bäckerei', 'comfort food', 'leicht']
    },
    {
        title: 'Rote-Linsen-Suppe',
        description: 'Wärmende Suppe mit roten Linsen, Karotten und Curry.',
        ingredients: ['rote Linsen', 'Karotten', 'Zwiebel', 'Gemüsebrühe', 'Currypulver'],
        duration: '30 Minuten',
        tags: ['gesund', 'suppe', 'vegan']
    }
];

const recipeContainer = document.getElementById('recipe-container');
const refreshButton = document.getElementById('refresh-button');
const recipeExampleList = document.getElementById('recipe-example-list');
const loadDailyDishButton = document.getElementById('load-daily-dish-button');
const dailyDishResult = document.getElementById('daily-dish-result');
const dailyDishTitle = document.getElementById('daily-dish-title');
const dailyDishDescription = document.getElementById('daily-dish-description');
const dailyDishIngredients = document.getElementById('daily-dish-ingredients');
const dailyDishInstructions = document.getElementById('daily-dish-instructions');
const dailyDishTags = document.getElementById('daily-dish-tags');
const downloadDailyDishButton = document.getElementById('download-daily-dish-button');
let currentDailyDishRecipe = null;

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
        .map(tag => `<span class="tag-pill">${tag.name}</span>`)
        .join('');

    currentDailyDishRecipe = recipe;
    if (downloadDailyDishButton) {
        downloadDailyDishButton.disabled = false;
    }

    const addToFavouritesButton = document.getElementById('add-to-favourites-button');
    if (addToFavouritesButton && recipe.id) {
        addToFavouritesButton.dataset.recipeId = recipe.id;
        addToFavouritesButton.innerHTML = '<span class="btn-icon">&#x2661;</span>Zu Favoriten hinzufügen';
        addToFavouritesButton.dataset.added = 'false';
        addToFavouritesButton.disabled = false;
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

function renderRecipe(recipe) {
    if (!recipeContainer) return;

    recipeContainer.innerHTML = `
        <h4>${recipe.title}</h4>
        <p>${recipe.description}</p>
        <ul>
            ${recipe.ingredients.map(item => `<li>${item}</li>`).join('')}
        </ul>
        <p><strong>Zubereitung:</strong> ${recipe.duration}</p>
        <p class="tag-list">Tags: ${recipe.tags.map(tag => `#${tag}`).join(' ')}</p>
    `;
}

function pickRandomRecipes(count) {
    const recipes = [...sampleRecipes];
    for (let i = recipes.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [recipes[i], recipes[j]] = [recipes[j], recipes[i]];
    }
    return recipes.slice(0, count);
}

function renderRecipeExamples(recipes) {
    if (!recipeExampleList) return;

    recipeExampleList.innerHTML = recipes.map(recipe => `
        <li>
            <strong>${recipe.title}</strong>
            <p>${recipe.description}</p>
        </li>
    `).join('');
}

if (refreshButton) {
    refreshButton.addEventListener('click', () => {
        renderRecipe(pickRandomRecipes(1)[0]);
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

renderRecipeExamples(pickRandomRecipes(2));

const addToFavouritesButton = document.getElementById('add-to-favourites-button');
if (addToFavouritesButton && loadDailyDishButton) {
    // Hover behavior: show "Aus Favoriten entfernen" on hover if added
    addToFavouritesButton.addEventListener('mouseenter', () => {
        if (addToFavouritesButton.dataset.added === 'true') {
            addToFavouritesButton.innerHTML = '<span class="btn-icon">&#x2665;</span>Aus Favoriten entfernen';
        }
    });

    addToFavouritesButton.addEventListener('mouseleave', () => {
        if (addToFavouritesButton.dataset.added === 'true') {
            addToFavouritesButton.innerHTML = '<span class="btn-icon">&#x2665;</span>In Favoriten gespeichert';
        }
    });

    addToFavouritesButton.addEventListener('click', async () => {
        const userId = loadDailyDishButton.dataset.userId;
        const recipeId = addToFavouritesButton.dataset.recipeId;
        if (!userId || !recipeId) return;

        const isAdded = addToFavouritesButton.dataset.added === 'true';

        try {
            if (!isAdded) {
                const res = await fetch(`/user/${userId}/favourites/${recipeId}`, { method: 'POST' });
                if (res.ok || res.status === 400) {
                    addToFavouritesButton.innerHTML = '<span class="btn-icon">&#x2665;</span>In Favoriten gespeichert';
                    addToFavouritesButton.dataset.added = 'true';
                }
            } else {
                const res = await fetch(`/user/${userId}/favourites/${recipeId}`, { method: 'DELETE' });
                if (res.ok || res.status === 400) {
                    addToFavouritesButton.innerHTML = '<span class="btn-icon">&#x2661;</span>Zu Favoriten hinzufügen';
                    addToFavouritesButton.dataset.added = 'false';
                }
            }
        } catch (e) {
            console.error('Fehler beim Aktualisieren der Favoriten:', e);
        }
    });
}
