# 🎨 ETL Tool - Custom Theme Guide

## 🌈 **Custom Color Palette**

Our ETL tool uses a carefully crafted color palette that provides excellent contrast and visual hierarchy in both light and dark modes.

### **Color Definitions**

```javascript
// Custom Color Palette
colors: {
  black: {
    DEFAULT: '#060505',  // Deep black
    100: '#010101',      // Darkest
    200: '#020202',
    300: '#030303',
    400: '#040404',
    500: '#060505',      // Base black
    600: '#3c3232',      // Warm dark gray
    700: '#736060',      // Medium gray
    800: '#a49292',      // Light gray
    900: '#d2c9c9'       // Lightest gray
  },
  white: {
    DEFAULT: '#ffffff',  // Pure white
    100: '#333333',      // Dark gray (for dark mode text)
    200: '#666666',
    300: '#999999',
    400: '#cccccc',
    500: '#ffffff',      // Base white
    600: '#ffffff',
    700: '#ffffff',
    800: '#ffffff',
    900: '#ffffff'
  },
  rojo: {
    DEFAULT: '#d82423',  // Primary red
    100: '#2b0707',      // Dark red
    200: '#560e0e',
    300: '#811515',
    400: '#ac1c1c',
    500: '#d82423',      // Base red
    600: '#e24c4c',      // Light red
    700: '#e97979',
    800: '#f0a6a6',
    900: '#f8d2d2'       // Lightest red
  },
  azure: {
    DEFAULT: '#d3e4e9',  // Light blue-gray
    100: '#1e343b',      // Dark blue-gray
    200: '#3b6876',
    300: '#5d9bad',
    400: '#98bfcb',
    500: '#d3e4e9',      // Base azure
    600: '#dce9ed',
    700: '#e5eff2',
    800: '#edf4f6',
    900: '#f6fafb'       // Lightest azure
  },
  vista: {
    DEFAULT: '#7f9ec3',  // Vista blue
    100: '#151f2c',      // Dark vista
    200: '#293e57',
    300: '#3e5d83',
    400: '#537cae',
    500: '#7f9ec3',      // Base vista
    600: '#98b1cf',
    700: '#b2c4db',
    800: '#ccd8e7',
    900: '#e5ebf3'       // Lightest vista
  }
}
```

---

## 🌓 **Dark/Light Mode Implementation**

### **Theme Context**
- **Location**: `src/contexts/ThemeContext.tsx`
- **Features**: 
  - Automatic system preference detection
  - LocalStorage persistence
  - Smooth transitions between themes
  - Ant Design theme integration

### **Theme Toggle**
- **Location**: `src/components/ThemeToggle.tsx`
- **Features**:
  - Sun/Moon icon toggle
  - Tooltip with current mode
  - Smooth animations

### **Usage Example**
```tsx
import { useTheme } from '@/contexts/ThemeContext';

const MyComponent = () => {
  const { isDark, toggleTheme } = useTheme();
  
  return (
    <div className={`transition-colors duration-300 ${
      isDark ? 'bg-vista-100 text-vista-300' : 'bg-white text-black-600'
    }`}>
      Content here
    </div>
  );
};
```

---

## 🎨 **Color Usage Guidelines**

### **Light Mode Color Mapping**
- **Primary**: `vista-600` (#537cae)
- **Secondary**: `azure-600` (#dce9ed)
- **Success**: `azure-500` (#d3e4e9)
- **Warning**: `rojo-700` (#e97979)
- **Error**: `rojo-500` (#d82423)
- **Background**: `azure-900` (#f6fafb)
- **Surface**: `white` (#ffffff)
- **Text Primary**: `black-600` (#3c3232)
- **Text Secondary**: `black-700` (#736060)

### **Dark Mode Color Mapping**
- **Primary**: `vista-400` (#537cae)
- **Secondary**: `azure-400` (#98bfcb)
- **Success**: `azure-400` (#98bfcb)
- **Warning**: `rojo-600` (#e24c4c)
- **Error**: `rojo-600` (#e24c4c)
- **Background**: `vista-100` (#151f2c)
- **Surface**: `vista-200` (#293e57)
- **Text Primary**: `vista-300` (#3e5d83)
- **Text Secondary**: `azure-300` (#5d9bad)

---

## 🎯 **Component Theming**

### **Buttons**
```tsx
// Primary Button
<Button 
  type="primary"
  className={`custom-button transition-all duration-300 ${
    isDark 
      ? 'bg-vista-500 hover:bg-vista-400 border-vista-500' 
      : 'bg-vista-600 hover:bg-vista-500 border-vista-600'
  }`}
>
  Primary Action
</Button>

// Success Button
<Button 
  className={`custom-button ${
    isDark 
      ? 'bg-azure-500 hover:bg-azure-400' 
      : 'bg-azure-600 hover:bg-azure-500'
  }`}
>
  Success Action
</Button>

// Danger Button
<Button 
  className={`custom-button ${
    isDark 
      ? 'bg-rojo-600 hover:bg-rojo-500' 
      : 'bg-rojo-500 hover:bg-rojo-400'
  }`}
>
  Danger Action
</Button>
```

### **Cards**
```tsx
<Card className={`custom-card transition-all duration-300 ${
  isDark ? 'bg-vista-200 border-vista-300' : 'bg-white border-azure-400'
}`}>
  Card content
</Card>
```

### **Status Indicators**
```tsx
// Success Status
<div className={`w-2 h-2 rounded-full ${
  isDark ? 'bg-azure-400' : 'bg-azure-600'
}`} />

// Error Status
<div className={`w-2 h-2 rounded-full ${
  isDark ? 'bg-rojo-600' : 'bg-rojo-500'
}`} />
```

---

## 🎨 **CSS Classes**

### **Custom Utility Classes**
```css
/* Animations */
.fade-in { animation: fadeIn 0.3s ease-in-out; }
.slide-up { animation: slideUp 0.3s ease-out; }

/* Components */
.custom-card { /* Enhanced card styling */ }
.custom-button { /* Enhanced button styling */ }

/* Gradients */
.bg-gradient-custom-light { /* Light mode gradient */ }
.bg-gradient-custom-dark { /* Dark mode gradient */ }

/* Status */
.status-indicator { /* Status indicator base */ }
.status-indicator.online::after { /* Online status */ }
.status-indicator.offline::after { /* Offline status */ }
```

### **Transition Classes**
All elements have smooth transitions:
```css
* {
  transition: background-color 300ms ease,
              border-color 300ms ease,
              color 300ms ease,
              box-shadow 300ms ease;
}
```

---

## 🌟 **Best Practices**

### **1. Always Use Theme-Aware Colors**
```tsx
// ✅ Good
className={`${isDark ? 'text-vista-300' : 'text-black-600'}`}

// ❌ Bad
className="text-gray-800"
```

### **2. Include Transitions**
```tsx
// ✅ Good
className="transition-colors duration-300"

// ❌ Bad - No transition
className="bg-blue-500"
```

### **3. Use Semantic Color Names**
```tsx
// ✅ Good - Semantic meaning
const primaryColor = isDark ? 'vista-400' : 'vista-600';
const errorColor = isDark ? 'rojo-600' : 'rojo-500';

// ❌ Bad - Hard to understand
const blueColor = '#537cae';
```

### **4. Test Both Modes**
Always test your components in both light and dark modes to ensure:
- Proper contrast ratios
- Readable text
- Consistent visual hierarchy
- Smooth transitions

---

## 🔧 **Customization**

### **Adding New Colors**
1. Add to `tailwind.config.js`
2. Update `ThemeContext.tsx` Ant Design theme
3. Add CSS variables if needed
4. Document usage guidelines

### **Modifying Existing Colors**
1. Update color values in `tailwind.config.js`
2. Test all components in both modes
3. Update documentation

---

## 🎯 **Theme Toggle Location**

The theme toggle button is located in the header of the ETL Dashboard:
- **Position**: Top-right corner
- **Icon**: Sun (light mode) / Moon (dark mode)
- **Tooltip**: Shows current mode and action
- **Persistence**: Saves preference to localStorage

---

## 🌈 **Visual Examples**

### **Light Mode**
- Clean, bright interface
- High contrast for readability
- Professional appearance
- Azure and Vista blue accents

### **Dark Mode**
- Easy on the eyes
- Reduced eye strain
- Modern appearance
- Warm color temperature

The theme system provides a cohesive, professional appearance that adapts to user preferences while maintaining excellent usability and accessibility standards.
