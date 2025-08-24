// Theme switching functionality for ResuMatch
// This file provides consistent theme switching across all pages

class ThemeManager {
    constructor() {
        this.currentTheme = 'light';
        this.init();
    }

    init() {
        // Load saved theme from localStorage
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(this.currentTheme);
        
        // Add event listeners
        this.addEventListeners();
        
        // Dispatch custom event for other scripts
        this.dispatchThemeEvent();
    }

    applyTheme(theme) {
        // Set theme attribute on document element
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update theme icon if it exists
        this.updateThemeIcon(theme);
        
        // Store current theme
        this.currentTheme = theme;
        
        // Save to localStorage
        localStorage.setItem('theme', theme);
        
        // Dispatch custom event
        this.dispatchThemeEvent();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    updateThemeIcon(theme) {
        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            
            // Update tooltip
            icon.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
        }
    }

    addEventListeners() {
        // Add click event to theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Listen for system theme changes (if supported)
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                // Only auto-switch if user hasn't manually set a preference
                if (!localStorage.getItem('theme')) {
                    const systemTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(systemTheme);
                }
            });
        }
    }

    dispatchThemeEvent() {
        // Dispatch custom event for other scripts to listen to
        const event = new CustomEvent('themeChanged', {
            detail: { theme: this.currentTheme }
        });
        document.dispatchEvent(event);
    }

    // Get current theme
    getCurrentTheme() {
        return this.currentTheme;
    }

    // Check if dark mode is active
    isDarkMode() {
        return this.currentTheme === 'dark';
    }

    // Set specific theme
    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.applyTheme(theme);
        }
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create global theme manager instance
    window.themeManager = new ThemeManager();
    
    // Add some additional utility functions
    window.toggleTheme = () => window.themeManager.toggleTheme();
    window.getCurrentTheme = () => window.themeManager.getCurrentTheme();
    window.isDarkMode = () => window.themeManager.isDarkMode();
    window.setTheme = (theme) => window.themeManager.setTheme(theme);
});

// Fallback for immediate access (in case script loads before DOM)
if (typeof window !== 'undefined') {
    // Simple fallback functions
    window.initTheme = function() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    };

    window.toggleTheme = function() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    };
}
