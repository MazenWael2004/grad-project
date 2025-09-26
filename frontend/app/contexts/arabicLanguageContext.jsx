import React, { createContext, useState,useContext } from "react";


export const ArabicLanguageContext = createContext();


export const ArabicLanguageProvider = ({children}) =>{
    const [isArabicLanguageOn,setIsArabicLanguageOn] = useState(false);

    const toggleArabic = ()=>{
        setIsArabicLanguageOn((prev)=> !prev);
    };


     return (
            <ArabicLanguageContext.Provider value={{ isArabicLanguageOn,toggleArabic }}>
              {children}
            </ArabicLanguageContext.Provider>
          );
}

export const useArabicLanguage = ()=> useContext(ArabicLanguageContext);