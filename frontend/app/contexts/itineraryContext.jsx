import React, { createContext, useState, useContext } from "react";

export const ItineraryContext = createContext();

export const ItineraryProvider = ({ children }) => {
  const [itineraryItems, setItineraryItems] = useState([]);

  const addToItineraryList = (item) => {
    setItineraryItems((prev) => {
      return [
        ...prev,
        {
          id: prev.length + 1,
          governorate_id: item.governorateId,
          userPreferences: item.userPreferences,
          // place_to_visit_id:
        },
      ];
    });
  };

  const updateItineraryItem = (id, updatedData) => {
    setItineraryItems((prev) => {
      return prev.map((item) => {
        if (item.id === id) {
          return { ...item, ...updatedData };
        }
        return item;
      });
    });
  };

  return (
    <ItineraryContext.Provider value={{ itineraryItems, addToItineraryList, updateItineraryItem }}>
      {children}
    </ItineraryContext.Provider>
  );
};


export const useItinerary = () => useContext(ItineraryContext);