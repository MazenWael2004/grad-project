import React, { createContext, useState,useContext } from "react";


export const UserTravelPreferencesContext = createContext();



export const UserTravelPreferencesProvider = ({children}) =>{
    const [userTravelPreferences,setUserTravelPreferences] = useState(null);
   
    // Handling the party options
    const addPartyId = (partyId) =>{
        setUserTravelPreferences((prev)=>{
          return{
            ...userTravelPreferences,
            partyId
        }
        })
        
    }

    // Handling the start and end trip dates.

    const addStartTripDate = (date)=>{
        setUserTravelPreferences((prev)=>{
            return{
                ...prev,
                startTripDate:date,
            }
        })
    }

    const addEndTripDate = (date)=>{
        setUserTravelPreferences((prev)=>{
            return{
                ...prev,
                endTripDate:date,
            }
        })
    }

    const addInterests = (interests) =>{
        setUserTravelPreferences((prev)=>{
            return{
                ...prev,
                interests:interests
            }
        })
    }

    const addBudgetId  = (budgetId)=>{
        setUserTravelPreferences((prev)=>{
            return{
                ...prev,
                budgetId
            }
        })
    }

     return (
        <UserTravelPreferencesContext.Provider value={{ userTravelPreferences,addPartyId,addStartTripDate,addEndTripDate,addInterests,addBudgetId }}>
          {children}
        </UserTravelPreferencesContext.Provider>
      );
};

export const useUserTravelPreferences = () => useContext(UserTravelPreferencesContext);