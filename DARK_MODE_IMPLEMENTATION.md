# Dark Mode Implementation for ResuMatch

This document describes the complete dark mode implementation for the ResuMatch Flask web interface.

## Overview

The dark mode feature provides users with a toggle between light and dark themes, with the following characteristics:

- **Toggle Button**: Moon (🌙) / Sun (☀️) icon in the navigation area
- **Persistent Storage**: User preference saved in localStorage
- **Smooth Transitions**: CSS transitions for theme switching
- **Comprehensive Coverage**: All pages and components support both themes
- **Default Theme**: Light mode is the default

## Implementation Details

### 1. CSS Variables System

The implementation uses CSS custom properties (variables) to define color schemes:

```css
:root {
    /* Light theme variables */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --border-color: #e9ecef;
    --shadow-color: rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] {
    /* Dark theme variables */
    --bg-primary: #121212;
    --bg-secondary: #1e1e1e;
    --text-primary: #e0e0e0;
    --text-secondary: #b0b0b0;
    --border-color: #404040;
    --shadow-color: rgba(0, 0, 0, 0.3);
}
```

### 2. Theme Toggle Button

Each page includes a theme toggle button positioned in the header:

```html
<button class="theme-toggle" id="themeToggle" title="Toggle dark mode">
    <i class="fas fa-moon" id="themeIcon"></i>
</button>
```

**Button Styling:**
- Circular design with backdrop blur effect
- Positioned absolutely in the top-right corner
- Smooth hover animations
- Icon changes between moon (🌙) and sun (☀️)

### 3. JavaScript Theme Management

The theme switching is handled by a `ThemeManager` class with the following features:

```javascript
class ThemeManager {
    constructor() {
        this.currentTheme = 'light';
        this.init();
    }

    init() {
        // Load saved theme from localStorage
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(this.currentTheme);
        this.addEventListeners();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateThemeIcon(theme);
    }
}
```

**Key Functions:**
- `initTheme()`: Initialize theme on page load
- `toggleTheme()`: Switch between light and dark themes
- `updateThemeIcon()`: Update the toggle button icon
- Local storage persistence
- Custom event dispatching for theme changes

### 4. Files Modified

#### HTML Templates
- `templates/index.html` - Main landing page
- `templates/form.html` - Resume form page
- `templates/view_resume.html` - Resume viewer page
- `templates/404.html` - 404 error page
- `templates/500.html` - 500 error page

#### CSS Files
- `static/css/theme.css` - Shared theme styles and variables

#### JavaScript Files
- `static/js/theme.js` - Theme management functionality

### 5. Color Scheme

#### Light Theme (Default)
- **Background**: #ffffff (White)
- **Secondary Background**: #f8f9fa (Light Gray)
- **Text Primary**: #212529 (Dark Gray)
- **Text Secondary**: #6c757d (Medium Gray)
- **Borders**: #e9ecef (Light Gray)
- **Shadows**: rgba(0, 0, 0, 0.1)

#### Dark Theme
- **Background**: #121212 (Very Dark Gray)
- **Secondary Background**: #1e1e1e (Dark Gray)
- **Text Primary**: #e0e0e0 (Off-White)
- **Text Secondary**: #b0b0b0 (Light Gray)
- **Borders**: #404040 (Medium Gray)
- **Shadows**: rgba(0, 0, 0, 0.3)

### 6. Component Coverage

The dark mode implementation covers all major UI components:

- **Forms**: Input fields, labels, buttons, checkboxes
- **Cards**: Containers, headers, content areas
- **Navigation**: Links, dropdowns, breadcrumbs
- **Alerts**: Success, error, warning messages
- **Tables**: Headers, rows, borders
- **Modals**: Overlays, content, headers
- **Buttons**: Primary, secondary, outline variants
- **Error Pages**: 404, 500 error displays

### 7. Accessibility Features

- **High Contrast**: Dark theme provides sufficient contrast ratios
- **Focus Indicators**: Clear focus states for keyboard navigation
- **Smooth Transitions**: Prevents jarring theme changes
- **Icon Labels**: Tooltips on theme toggle button
- **Semantic Colors**: Colors maintain meaning across themes

### 8. Browser Compatibility

- **Modern Browsers**: Full support for CSS variables and modern JavaScript
- **Fallback Support**: Graceful degradation for older browsers
- **Local Storage**: Persistent theme preference storage
- **CSS Transitions**: Smooth animations where supported

### 9. Usage Instructions

#### For Users
1. Look for the moon (🌙) icon in the top-right corner of any page
2. Click the icon to toggle between light and dark themes
3. Your preference will be remembered across visits
4. The icon changes to sun (☀️) when in dark mode

#### For Developers
1. Include the theme CSS and JS files in your templates
2. Add the theme toggle button HTML where needed
3. Use CSS variables for colors instead of hardcoded values
4. Test both themes to ensure proper contrast and readability

### 10. Customization

#### Adding New Colors
To add new color variables, update the CSS variables in `static/css/theme.css`:

```css
:root {
    --new-color: #your-light-color;
}

[data-theme="dark"] {
    --new-color: #your-dark-color;
}
```

#### Theme-Specific Styles
Use the `[data-theme="dark"]` selector for dark-mode-specific styles:

```css
[data-theme="dark"] .custom-component {
    background-color: var(--bg-secondary);
    border-color: var(--border-color);
}
```

#### JavaScript Integration
Listen for theme change events:

```javascript
document.addEventListener('themeChanged', function(e) {
    const theme = e.detail.theme;
    // Handle theme change
    console.log('Theme changed to:', theme);
});
```

### 11. Testing

#### Manual Testing
1. Navigate to each page and verify theme toggle works
2. Check that all elements are properly styled in both themes
3. Verify theme persistence across page refreshes
4. Test on different screen sizes and devices

#### Automated Testing
Consider adding tests for:
- Theme toggle functionality
- Local storage persistence
- CSS variable application
- Component styling in both themes

### 12. Future Enhancements

Potential improvements for future versions:

- **System Theme Detection**: Auto-switch based on OS preference
- **Custom Color Schemes**: User-defined color palettes
- **Animation Preferences**: Reduce motion options
- **High Contrast Mode**: Additional accessibility theme
- **Theme Scheduling**: Auto-switch themes at certain times

## Conclusion

The dark mode implementation provides a comprehensive, user-friendly theme switching system that enhances the user experience while maintaining accessibility and performance. The modular design makes it easy to extend and customize for future needs.

