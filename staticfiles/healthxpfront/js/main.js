// Wait for DOM content to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Mobile navigation toggle - REMOVED
    // No longer adding the mobile hamburger menu 

    // Handle dropdown menus
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            // Only prevent default on mobile
            if (window.innerWidth <= 768) {
                e.preventDefault();

                const parent = this.parentElement;
                parent.classList.toggle('active');

                // Close other dropdowns
                dropdownToggles.forEach(otherToggle => {
                    if (otherToggle !== toggle) {
                        otherToggle.parentElement.classList.remove('active');
                    }
                });
            }
        });
    });

    // Search functionality
    const searchIcon = document.querySelector('.search-icon');

    if (searchIcon) {
        searchIcon.addEventListener('click', function () {
            // Create search overlay if it doesn't exist
            let searchOverlay = document.querySelector('.search-overlay');

            if (!searchOverlay) {
                searchOverlay = document.createElement('div');
                searchOverlay.classList.add('search-overlay');

                const searchForm = document.createElement('div');
                searchForm.classList.add('search-form');

                searchForm.innerHTML = `
                    <button class="close-search"><i class="fas fa-times"></i></button>
                    <form>
                        <input type="text" placeholder="Search..." autofocus>
                        <button type="submit"><i class="fas fa-search"></i></button>
                    </form>
                `;

                searchOverlay.appendChild(searchForm);
                document.body.appendChild(searchOverlay);

                // Close search overlay
                const closeSearch = searchOverlay.querySelector('.close-search');
                closeSearch.addEventListener('click', function () {
                    searchOverlay.classList.remove('show');
                });

                // Handle search form submission
                const form = searchForm.querySelector('form');
                form.addEventListener('submit', function (e) {
                    e.preventDefault();
                    const searchTerm = this.querySelector('input').value;
                    if (searchTerm.trim() !== '') {
                        // Perform search (this would be replaced with actual search functionality)
                        console.log('Searching for:', searchTerm);

                        // For demonstration, we'll just close the overlay
                        searchOverlay.classList.remove('show');
                    }
                });
            }

            // Show the overlay
            searchOverlay.classList.add('show');
        });
    }

    // Add CSS for the search overlay
    const style = document.createElement('style');
    style.textContent = `
        .search-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        
        .search-overlay.show {
            opacity: 1;
            visibility: visible;
        }
        
        .search-form {
            width: 80%;
            max-width: 600px;
            position: relative;
        }
        
        .close-search {
            position: absolute;
            top: -40px;
            right: 0;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
        }
        
        .search-form form {
            display: flex;
        }
        
        .search-form input {
            flex: 1;
            padding: 15px;
            font-size: 18px;
            border: none;
            border-radius: 4px 0 0 4px;
        }
        
        .search-form button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0 20px;
            border-radius: 0 4px 4px 0;
            cursor: pointer;
        }
        
        @media (max-width: 768px) {
            /* Removed mobile hamburger menu styles */
            
            .nav-menu {
                display: flex;
                width: 100%;
            }
            
            .nav-menu li {
                width: auto;
            }
            
            .nav-menu a {
                width: auto;
                padding: 15px;
            }
        }
    `;

    document.head.appendChild(style);

    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.classList.add('back-to-top');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTopButton);

    // Show/hide back to top button based on scroll position
    window.addEventListener('scroll', function () {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });

    // Scroll to top when button is clicked
    backToTopButton.addEventListener('click', function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Add CSS for back to top button
    const backToTopStyle = document.createElement('style');
    backToTopStyle.textContent = `
        .back-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
            z-index: 999;
        }
        
        .back-to-top.show {
            opacity: 1;
            visibility: visible;
        }
    `;

    document.head.appendChild(backToTopStyle);
}); 