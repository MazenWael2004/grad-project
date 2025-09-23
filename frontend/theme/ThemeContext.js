// import React, { createContext, useState, useEffect } from "react";
// import { Appearance } from "react-native";

// export const ThemeContext = createContext();

// export const ThemeProvider = ({ children }) => {
  
//   const [theme, setTheme] = useState(Appearance.getColorScheme() || "light");

  
//   useEffect(() => {
//     const subscription = Appearance.addChangeListener(({ colorScheme }) => {
//       setTheme(colorScheme);
//     });
//     return () => subscription.remove();
//   }, []);

 
//   const toggleTheme = () => {
//     setTheme(prev => (prev === "light" ? "dark" : "light"));
//   };

//   return (
//     <ThemeContext.Provider value={{ theme, toggleTheme }}>
//       {children}
//     </ThemeContext.Provider>
//   );
// };
