function updateTypeSpecificFields(selectedType) {
    const allTypeFields = document.querySelectorAll('[data-type-field]');
    allTypeFields.forEach(field => {
        const fieldContainer =
            field.closest('.field') ||
            field.closest('.form-group') ||
            field.closest('.mb-3') ||
            field.closest('.row');

        if (fieldContainer) {
            fieldContainer.classList.add('d-none');
            // Clear field value when hiding
            if (field.tagName === 'SELECT') {
                field.selectedIndex = 0;
            } else {
                field.value = '';
            }
        }
    });

    if (selectedType) {
        const typeFields = document.querySelectorAll(`[data-type-field="${selectedType}"]`);
        typeFields.forEach(field => {
            const fieldContainer =
                field.closest('.field') ||
                field.closest('.form-group') ||
                field.closest('.mb-3') ||
                field.closest('.row');

            if (fieldContainer) {
                fieldContainer.classList.remove('d-none');
            }
        });
    }
}


// Initialize form when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("Segment form script loaded");
    const segmentTypeField = document.querySelector('select[name="segment_type"]') || 
                            document.querySelector('#id_segment_type');
    
    if (segmentTypeField) {
        // Set up initial state
        updateTypeSpecificFields(segmentTypeField.value);
        
        // Handle changes
        segmentTypeField.addEventListener('change', function() {
            updateTypeSpecificFields(this.value);
        });
    }
});

console.log("FILE: segment_form.js loaded");