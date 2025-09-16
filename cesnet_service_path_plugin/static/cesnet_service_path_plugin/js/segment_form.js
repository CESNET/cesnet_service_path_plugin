function updateTypeSpecificFields(selectedType) {
    const allTypeFields = document.querySelectorAll('[data-type-field]');
    
    // First, hide all type-specific fields but DON'T clear their values during initialization
    allTypeFields.forEach(field => {
        const fieldContainer =
            field.closest('.field') ||
            field.closest('.form-group') ||
            field.closest('.mb-3') ||
            field.closest('.row');

        if (fieldContainer) {
            fieldContainer.classList.add('d-none');
            console.log('Hiding field:', field.name, 'current value:', field.value);
            
            // IMPORTANT: Don't clear values - let Django's initial values remain intact
            // The form initialization should preserve existing values
        }
    });

    // Then show fields for the selected type
    if (selectedType) {
        const typeFields = document.querySelectorAll(`[data-type-field="${selectedType}"]`);
        console.log(`Showing ${typeFields.length} fields for type:`, selectedType);
        
        typeFields.forEach(field => {
            const fieldContainer =
                field.closest('.field') ||
                field.closest('.form-group') ||
                field.closest('.mb-3') ||
                field.closest('.row');

            if (fieldContainer) {
                fieldContainer.classList.remove('d-none');
                console.log('Showing field:', field.name, 'with value:', field.value);
            }
        });
    }
}

// Initialize form when page loads
document.addEventListener('DOMContentLoaded', function() {
    const segmentTypeField = document.querySelector('select[name="segment_type"]') || 
                            document.querySelector('#id_segment_type');
    
    if (segmentTypeField) {
        console.log('Found segment type field with value:', segmentTypeField.value);
        
        // Set up initial state - show fields for current type
        updateTypeSpecificFields(segmentTypeField.value);
        
        // Handle changes
        segmentTypeField.addEventListener('change', function() {
            console.log('Segment type changed to:', this.value);
            updateTypeSpecificFields(this.value);
        });
    } else {
        console.error('Segment type field not found');
    }
    
    // Debug: List all type-specific fields found
    const allTypeFields = document.querySelectorAll('[data-type-field]');
    console.log('All type-specific fields found:');
    allTypeFields.forEach(field => {
        console.log(`- ${field.name}: type="${field.getAttribute('data-type-field')}", value="${field.value}"`);
    });
});
