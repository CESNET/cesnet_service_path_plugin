function updateTypeSpecificFields(selectedType) {
    // Hide all type-specific fields first
    const allTypeFields = document.querySelectorAll('.type-field');
    allTypeFields.forEach(field => {
        const fieldContainer = field.closest('.field') || field.closest('.form-group') || field.closest('.mb-3');
        if (fieldContainer) {
            fieldContainer.style.display = 'none';
            // Clear field value when hiding
            if (field.tagName === 'SELECT') {
                field.selectedIndex = 0;
            } else {
                field.value = '';
            }
        }
    });
    
    // Show fields for selected type
    if (selectedType) {
        const typeFields = document.querySelectorAll(`.type-${selectedType}`);
        typeFields.forEach(field => {
            const fieldContainer = field.closest('.field') || field.closest('.form-group') || field.closest('.mb-3');
            if (fieldContainer) {
                fieldContainer.style.display = 'block';
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