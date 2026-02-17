import React, { createContext, useState,useContext } from 'react';
import subscriptions from '../../constants/subscriptions'

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({
    userId: null,
    name: '',
    email: '',
    password: '',
    paymentMethods: [],
    currentSubscription: subscriptions[0],
    country: '',
    isLoggedIn: false,
    role: 'user',
    profilePic:null,
    exchangeRate: 1,
  });

  const login = (userData) => {
    setUser({ ...userData, isLoggedIn: true });
  };

  const logout = () => {
    setUser({ userId: null, name: '', email: '', country: '', isLoggedIn: false });
  };

  return (
    <UserContext.Provider value={{ user, login, logout,setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = ()=> useContext(UserContext);