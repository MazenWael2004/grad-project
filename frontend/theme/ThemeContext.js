import React, { createContext, useState, /* useEffect */ } from "react";
//import { Appearance } from "react-native";

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  
  const [theme, setTheme] = useState(/*Appearance.getColorScheme() ||*/ "Light");

  
 /* useEffect(() => {
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      setTheme(colorScheme);
    });
    return () => subscription.remove();
  }, []);

  */

 
  const toggleTheme = () => {
    setTheme(prev => (prev === "Light" ? "Dark" : "Light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme,setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
