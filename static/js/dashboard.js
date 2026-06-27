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

renderRecipeExamples(pickRandomRecipes(2));
