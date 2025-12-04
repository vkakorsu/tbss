(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('searchbar');
        if (!searchInput) return;
        
        let debounceTimer;
        const debounceDelay = 300; // ms
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                // Submit the search form
                searchInput.closest('form').submit();
            }, debounceDelay);
        });
    });
})();
