import React, { createContext, useState, useContext } from "react";

export const RegisterFormContext = createContext();

export const RegisterFormProvider = ({ children }) => {
  const [registerFormData, setRegisterFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    country: "",
    password: "",
    confirmPassword: "",
  });



  return (
    <RegisterFormContext.Provider value={{ setRegisterFormData,registerFormData }}>
      {children}
    </RegisterFormContext.Provider>
  );
};


export const useRegisterFormContext = ()=> useContext(RegisterFormContext);