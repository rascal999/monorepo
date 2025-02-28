document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.querySelector('.screenshot-gallery');
    const navDots = document.querySelectorAll('.nav-dot');
    const items = document.querySelectorAll('.screenshot-item');
    
    if (!gallery || !navDots.length || !items.length) return;
    
    // Set up navigation dots
    navDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            // Calculate the scroll position
            const scrollPosition = gallery.clientWidth * index;
            
            // Scroll to the position
            gallery.scrollTo({
                left: scrollPosition,
                behavior: 'smooth'
            });
            
            // Update active dot
            updateActiveDot(index);
        });
    });
    
    // Update active dot based on scroll position
    function updateActiveDot(activeIndex) {
        navDots.forEach((dot, index) => {
            if (index === activeIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    // Handle scroll events to update active dot
    gallery.addEventListener('scroll', () => {
        const scrollPosition = gallery.scrollLeft;
        const itemWidth = gallery.clientWidth;
        
        // Calculate which item is most visible
        const activeIndex = Math.round(scrollPosition / itemWidth);
        
        // Update the active dot
        updateActiveDot(activeIndex);
    });
    
    // Auto-advance the gallery every 5 seconds
    let currentIndex = 0;
    
    function autoAdvance() {
        currentIndex = (currentIndex + 1) % items.length;
        
        // Calculate the scroll position
        const scrollPosition = gallery.clientWidth * currentIndex;
        
        // Scroll to the position
        gallery.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
        });
        
        // Update active dot
        updateActiveDot(currentIndex);
    }
    
    // Start auto-advance
    const intervalId = setInterval(autoAdvance, 5000);
    
    // Pause auto-advance when user interacts with gallery
    gallery.addEventListener('mouseenter', () => {
        clearInterval(intervalId);
    });
    
    // Resume auto-advance when user leaves gallery
    gallery.addEventListener('mouseleave', () => {
        clearInterval(intervalId);
        intervalId = setInterval(autoAdvance, 5000);
    });
});