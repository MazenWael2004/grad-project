import React, {
  createContext,
  useState,
  useContext,
  useEffect,
} from "react";
import subscriptions from '../../constants/subscriptions'
import AsyncStorage from "@react-native-async-storage/async-storage";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({
    userId: null,
    first_name: "",
    last_name: "",
    email: "",
    subscriptionID: 1,
    country: "",
    access: "",
    refresh: "",
    isLoggedIn: false,
    role: "user",
    profilePic: null,
    exchangeRate: 1,
    phoneNumber: "",
  });


  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUser = await AsyncStorage.getItem("user");
        const access = await AsyncStorage.getItem("access");
        const refresh = await AsyncStorage.getItem("refresh");

        console.log("Stored User:", storedUser);
        console.log("Stored Access:", access);
        console.log("Stored Refresh:", refresh);

        if (storedUser) {
          setUser({
            ...JSON.parse(storedUser),
            isLoggedIn: true,
          });
        }
      } catch (error) {
        console.log(error);
      }
    };

    loadUser();
  }, []);

  const login = async (userData) => {
  await AsyncStorage.setItem("access", userData.access);
  await AsyncStorage.setItem("refresh", userData.refresh);
  console.log("access:",userData.access)
  console.log("refresh:",userData.refresh)
  await AsyncStorage.setItem("user", JSON.stringify(userData));

  setUser({
    ...userData,
    isLoggedIn: true,
  });
};

const logout = async () => {
  await AsyncStorage.removeItem("access");
  await AsyncStorage.removeItem("refresh");
  await AsyncStorage.removeItem("user");

  setUser({
    userId: null,
    first_name: "",
    last_name: "",
    email: "",
    country: "",
    access: "",
    refresh: "",
    phoneNumber: "",
    isLoggedIn: false,
  });
};

  return (
    <UserContext.Provider value={{ user, login, logout,setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = ()=> useContext(UserContext);