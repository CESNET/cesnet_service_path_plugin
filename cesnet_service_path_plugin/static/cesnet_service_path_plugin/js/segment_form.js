function updateTypeSpecificFields(selectedType) {
    const allTypeFields = document.querySelectorAll('[data-type-field]');

    allTypeFields.forEach(field => {
        const fieldContainer =
            field.closest('.field') ||
            field.closest('.form-group') ||
            field.closest('.mb-3') ||
            field.closest('.row');
        if (fieldContainer) fieldContainer.classList.add('d-none');
    });

    if (selectedType) {
        document.querySelectorAll(`[data-type-field="${selectedType}"]`).forEach(field => {
            const fieldContainer =
                field.closest('.field') ||
                field.closest('.form-group') ||
                field.closest('.mb-3') ||
                field.closest('.row');
            if (fieldContainer) fieldContainer.classList.remove('d-none');
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const segmentTypeField =
        document.querySelector('select[name="segment_type"]') ||
        document.querySelector('#id_segment_type');

    if (!segmentTypeField) return;

    updateTypeSpecificFields(segmentTypeField.value);
    segmentTypeField.addEventListener('change', function () {
        updateTypeSpecificFields(this.value);
    });
});
