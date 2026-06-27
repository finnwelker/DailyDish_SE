const api = {
    async fetchRecipe() {
        return {
            title: 'Sommer-Pasta',
            description: 'Ein schnelles Pastagericht mit Tomaten, Knoblauch und frischem Basilikum.',
            ingredients: ['Pasta', 'Tomaten', 'Knoblauch', 'Olivenöl', 'Basilikum'],
            duration: '20 Minuten',
            tags: ['schnell', 'frisch', 'vegetarisch']
        };
    }
};
