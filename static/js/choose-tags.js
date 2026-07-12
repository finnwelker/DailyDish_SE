document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('tag-selection-form');
    if (!form) {
        return;
    }

    const selectedTagIds = new Set();
    const buttons = Array.from(form.querySelectorAll('.tag-pill-button'));

    buttons.forEach((button) => {
        if (button.classList.contains('selected')) {
            selectedTagIds.add(button.dataset.tagId);
        }

        button.addEventListener('click', () => {
            const tagId = button.dataset.tagId;
            if (selectedTagIds.has(tagId)) {
                selectedTagIds.delete(tagId);
                button.classList.remove('selected');
            } else {
                selectedTagIds.add(tagId);
                button.classList.add('selected');
            }
        });
    });

    form.addEventListener('submit', () => {
        form.querySelectorAll('input[name="tag_ids"]').forEach((input) => input.remove());

        selectedTagIds.forEach((tagId) => {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'tag_ids';
            hiddenInput.value = tagId;
            form.appendChild(hiddenInput);
        });
    });
});
