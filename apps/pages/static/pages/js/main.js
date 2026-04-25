document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggle = document.querySelector('.dropdown-section-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
        // Functionality for the dropdown menu
        // Handle the click on the toggle icon
        dropdownToggle.addEventListener('click', function(event) {
            event.stopPropagation();

            // Toggle the active classes
            dropdownToggle.classList.toggle('active');
            dropdownMenu.classList.toggle('active');
        });

        
        document.addEventListener('click', function(event) {
            // Check if the click was outside the toggle icon or the menu
            const isClickInside = dropdownToggle.contains(event.target) ||
                dropdownMenu.contains(event.target);

            // Remove active classes
            if (!isClickInside) {
                dropdownToggle.classList.remove('active');
                dropdownMenu.classList.remove('active');
            }
        });
    }
});