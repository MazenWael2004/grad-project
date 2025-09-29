import React, { createContext, useState, useContext } from "react";

export const SavedListContext = createContext();

export const SavedListProvider = ({ children }) => {
  const [savedList, setSavedList] = useState([]);

  const addToSavedList = (item) => {
    setSavedList((prev) => {
      return [
        ...prev,
        item
      ];
    });
  };

  const removeFromSavedList = (itemId) => {
    setSavedList((prevItems) =>
      prevItems.filter((item) => item.id !== itemId)
    );
  }


  return (
    <SavedListContext.Provider value={{ savedList, addToSavedList,removeFromSavedList }}>
      {children}
    </SavedListContext.Provider>
  );
};


export const useSavedList = ()=> useContext(SavedListContext);