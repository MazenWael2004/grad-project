import { useLocalSearchParams } from "expo-router";
import { useRegisterFormContext } from "../contexts/registerFormContext";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  Image,
  TouchableOpacity,
} from "react-native";
import React, { use, useEffect, useState } from "react";
import { hide } from "expo-splash-screen";
import { useRouter } from "expo-router";
import axios from "axios";
import Constants from "expo-constants";
import { Alert } from "react-native";
import { useUser } from "../contexts/userContext";



const { API_BASE_URL } = Constants.expoConfig.extra;
console.log(`${API_BASE_URL}/register/`);

const Register = () => {
  // States...
  const { user, setUser } = useUser();
  const [email, setEmail] = useState("");
  const { registerFormData, setRegisterFormData } = useRegisterFormContext();
  const [password, setPassword] = useState("");
  const { country } = useLocalSearchParams();

  const [fullName, setFullName] = useState({
    firstName: "",
    lastName: "",
  });
  const [confirmPassword, setConfirmPassword] = useState("");
  const [hidePassword, setHidePassword] = useState(true);
  const [isPasswordCorrect, setIsPasswordCorrect] = useState(true);
  const [isEmailValidated, setIsEmailValidated] = useState(true);
  const [isFirstNameRequired, setIsFirstNameRequired] = useState(true);
  const [isLastNameRequired, setIsLastNameRequired] = useState(true);
  const [isPasswordRequired, setIsPasswordRequired] = useState(true);
  const [isConfirmPasswordRequired, setIsConfirmPasswordRequired] =
    useState(true);
  const [isCountryRequired, setIsCountryRequired] = useState(true);
  const [isEmailRequired, setIsEmailRequired] = useState(true);
  const [isPasswordValidated, setIsPasswordValidated] = useState(true);
  const [selectedCountry, setSelectedCountry] = useState(null);

  const countries = [
    { label: "Egypt", value: "EG" },
    { label: "France", value: "FR" },
    { label: "Japan", value: "JP" },
    { label: "Brazil", value: "BR" },
    // Add more countries as needed
  ];

  //-----------------------------------------------------------------
  console.log("Register Form Data: ", JSON.stringify(registerFormData, null, 2));

  useEffect(() => {
    setSelectedCountry(country);
  }, [country]);

  // Form Handler Functions.....
  const handleFirstNameChange = (text) => {
    setIsFirstNameRequired(true);
    setFullName((prevFullName) => ({
      ...prevFullName,
      firstName: text,
    }));

    // console.log("Full Name: " + text + fullName.lastName);
    setRegisterFormData((prev) => {
      return {
        ...prev,
        firstName: text,
        lastName: fullName.lastName,
      };
    });
  };

  const handleLastNameChange = (text) => {
    setIsLastNameRequired(true);
    setFullName((prevFullName) => ({
      ...prevFullName,
      lastName: text,
    }));

    setRegisterFormData((prev) => {
      return {
        ...prev,
        firstName: fullName.firstName,
        lastName: text,
      };
    });

    // console.log("Full Name: " + fullName.firstName + text);
  };

  // Creates a new object by copying all properties from the previous state and replacing the `firstName` property with the new text value.

  const handleEmailChange = (text) => {
    setIsEmailRequired(true);
    setEmail(text);
    // console.log("Email: ", text);
    setRegisterFormData((prev) => {
      return {
        ...prev,
        email: text,
      };
    });
  };

  const handlePasswordChange = (text) => {
    setIsPasswordRequired(true);
    setPassword(text);
    // console.log("Password: " + text);
    setRegisterFormData((prev) => {
      return {
        ...prev,
        password: text,
      };
    });
  };

  const handleConfirmPasswordChange = (text) => {
    setConfirmPassword(text);
    setIsConfirmPasswordRequired(true);
    // console.log("Confirm Password: " + text);
    setRegisterFormData((prev) => {
      return {
        ...prev,
        confirmPassword: text,
      };
    });
  };

  const validateForm = () => {
  let valid = true;

  // First Name
  if (!registerFormData.firstName || registerFormData.firstName.trim() === "") {
    setIsFirstNameRequired(false);
    valid = false;
  } else {
    setIsFirstNameRequired(true);
  }

  // Last Name
  if (!registerFormData.lastName || registerFormData.lastName.trim() === "") {
    setIsLastNameRequired(false);
    valid = false;
  } else {
    setIsLastNameRequired(true);
  }

  // Email
  if (!registerFormData.email || registerFormData.email.trim() === "") {
    setIsEmailRequired(false);
    valid = false;
  } else {
    setIsEmailRequired(true);
    let regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!regex.test(registerFormData.email)) {
      setIsEmailValidated(false);
      valid = false;
    } else {
      setIsEmailValidated(true);
    }
  }

  // Country
  if (!registerFormData.country || registerFormData.country.trim() === "") {
    setIsCountryRequired(false);
    valid = false;
  } else {
    setIsCountryRequired(true);
  }

  // Password
  if (!registerFormData.password || registerFormData.password.trim() === "") {
    setIsPasswordRequired(false);
    valid = false;
    
  } else {
    setIsPasswordRequired(true);
    if (registerFormData.password.length < 8) {
      setIsPasswordValidated(false);
      valid = false;
    } else {
      setIsPasswordValidated(true);
    }
  }

  // Confirm Password
  if (
    !registerFormData.confirmPassword ||
    registerFormData.confirmPassword.trim() === ""
  ) {
    setIsConfirmPasswordRequired(false);
    valid = false;
  } else {
    setIsConfirmPasswordRequired(true);
    if (registerFormData.confirmPassword !== registerFormData.password) {
      setIsPasswordCorrect(false);
      valid = false;
    } else {
      setIsPasswordCorrect(true);
    }
  }

  return valid;
};

const handleSubmitButton = async () => {
  if (!validateForm()) {
    console.log("Validation failed ❌");
    Alert.alert("Warning", "Please fix errors before submitting.");
    return;
  }

  console.log("Validation passed ✅");
  console.log("Submitting form with data: ", registerFormData); // Debug log to check form data before API call
  // Proceed with API request
  try {
    const response = await axios.post(`http://10.187.16.161:8000/api/accounts/register/`, {
      first_name: registerFormData.firstName,
      last_name: registerFormData.lastName,
      email: registerFormData.email,
      password: registerFormData.password,
      country: registerFormData.country, // Added this...
    });

    if (response.status === 201) {
      const user = response.data.user;
      const token = response.data.token;
      Alert.alert("Success", "Account created successfully!");
      // Setting user context after registering...
      setUser({
       userId:user.id,
       first_name:user.first_name,
       last_name:user.last_name,
       email:user.email,
       country:user.country,
       phoneNumber:user.phone_number,
       token,
      })
      router.replace("/main/");
    }
  } catch (error) {
    console.error(error.response?.data || error.message);
    Alert.alert("Error", "Registration failed. Try again.");
  }
};



  const router = useRouter();
  return (
    <>
      <TouchableOpacity
        style={{
          position: "absolute",
          top: 50,
          left: 20,
          zIndex: 1,
          backgroundColor: "#e6e1e1ff",
          borderRadius: 20,
          padding: 5,
        }}
        onPress={() => router.back()}
      >
        <Image
          source={require("../../assets/images/back.png")}
          style={{ width: 30, height: 30 }}
          onPress={() => router.back()}
        />
      </TouchableOpacity>
      <View
        style={{
          flex: 1,
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#fff",
          flexDirection: "column",
        }}
      >
        <Text
          style={{
            fontFamily: "Poppins-Bold",
            fontSize: 24,
            color: "#333",
          }}
        >
          Register
        </Text>
        <View style={styles.loginWrapper}>
          <View style={{ flexDirection: "row", gap: 10, width: "100%" }}>
            <View style={{ flex: 1, marginBottom: 10 }}>
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 16,
                  color: "#333",
                  marginBottom: 10,
                }}
              >
                First Name
                <Text style={{ color: "red" }}> *</Text>
              </Text>
              <TextInput
                placeholder="John"
                style={[
                  {
                    height: 50,
                    borderColor: "#ccc",
                    borderWidth: 1,
                    paddingHorizontal: 10,
                    borderRadius: 10,
                    fontFamily: "Poppins-Regular",
                  },

                  !isFirstNameRequired && styles.errorInput,
                ]}
                onChangeText={handleFirstNameChange}
                value={registerFormData?.firstName}
              />
              {!isFirstNameRequired && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Field required.
                </Text>
              )}
            </View>

            <View style={{ flex: 1 }}>
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 16,
                  color: "#333",
                  marginBottom: 10,
                }}
              >
                Last Name
                <Text style={{ color: "red" }}> *</Text>
              </Text>
              <TextInput
                placeholder="Doe"
                style={[
                  {
                    height: 50,
                    borderColor: "#ccc",
                    borderWidth: 1,
                    paddingHorizontal: 10,
                    borderRadius: 10,
                    fontFamily: "Poppins-Regular",
                  },
                  !isLastNameRequired && styles.errorInput,
                ]}
                onChangeText={handleLastNameChange}
                value={registerFormData?.lastName}
              />
              {!isLastNameRequired && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Field required.
                </Text>
              )}
            </View>
          </View>

          <View style={styles.inputWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 16,
                color: "#333",
              }}
            >
              E-mail
              <Text style={{ color: "red" }}> *</Text>
            </Text>
            <View>
              <TextInput
                placeholder="Enter your email"
                style={[
                  {
                    height: 50,
                    borderColor: "#ccc",
                    borderWidth: 1,
                    paddingHorizontal: 10,
                    borderRadius: 10,
                    marginBottom: 2,
                    fontFamily: "Poppins-Regular",
                    position: "relative",
                  },
                  (!isEmailValidated || !isEmailRequired) && styles.errorInput,
                ]}
                value={registerFormData?.email}
                onChangeText={handleEmailChange}
              />
              {!isEmailValidated && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Invalid Email address. Please Enter a valid one.
                </Text>
              )}

              {!isEmailRequired && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Field required.
                </Text>
              )}
            </View>
          </View>

          <View style={styles.inputWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 16,
                color: "#333",
              }}
            >
              Country
              <Text style={{ color: "red" }}> *</Text>
            </Text>
            <View>
              <TouchableOpacity
                onPress={() => router.push("countryPicker")}
                style={[
                  {
                    height: 50,
                    borderColor: "#ccc",
                    borderWidth: 1,
                    paddingHorizontal: 10,
                    borderRadius: 10,
                    backgroundColor: "#e4e2e2ff",
                    marginBottom: 2,
                    fontFamily: "Poppins-Regular",
                    position: "relative",
                    paddingTop: 15,
                    paddingLeft: 10,
                  },
                  !isCountryRequired && styles.errorInput,
                ]}
              >
                
                <View
                  style={{
                    flexDirection: "row",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <Text style={{ fontFamily: "Poppins-Medium", color: "#333" }}>
                    {selectedCountry !== undefined
                      ? selectedCountry
                      : "Select your country"}
                  </Text>
                  <Image
                    source={require("../../assets/images/right-arrow.png")}
                    style={{
                      width: 15,
                      height: 15,
                      resizeMode: "contain",
                      tintColor: "#333",
                    }}
                  />
                </View>
              </TouchableOpacity>
              {!isCountryRequired && (
                  <Text
                    style={{
                      color: "red",
                      fontFamily: "Poppins-Medium",
                      fontSize: 13,
                      marginTop: 5,
                    }}
                  >
                    Field required.
                  </Text>
                )}
            </View>
          </View>

          <View style={styles.inputWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 16,
                color: "#333",
              }}
            >
              Password
              <Text style={{ color: "red" }}> *</Text>
            </Text>
            <View>
              <TextInput
                placeholder="Enter your password"
                style={[
                  {
                    height: 50,
                    borderColor: "#ccc",
                    borderWidth: 1,
                    paddingHorizontal: 10,
                    borderRadius: 10,
                    fontFamily: "Poppins-Regular",
                    position: "relative",
                  },
                  (!isPasswordRequired || !isPasswordValidated) &&
                    styles.errorInput,
                ]}
                secureTextEntry={hidePassword ? true : false}
                value={registerFormData?.password}
                onChangeText={handlePasswordChange}
              />
              {!isPasswordValidated && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Password must be at least 8 characters.
                </Text>
              )}

              {!isPasswordRequired && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Field required.
                </Text>
              )}
              <TouchableOpacity
                onPress={() => setHidePassword(!hidePassword)}
                style={{
                  position: "absolute",
                  right: 10,
                  top: 15,
                  width: 20,
                  height: 20,
                }}
              >
                <Image
                  source={
                    hidePassword
                      ? require("../../assets/images/hide.png")
                      : require("../../assets/images/show.png")
                  }
                  style={{
                    width: 20,
                    height: 20,
                    resizeMode: "contain",
                  }}
                />
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.inputWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 16,
                color: "#333",
              }}
            >
              Confirm Password
              <Text style={{ color: "red" }}> *</Text>
            </Text>
            <View>
              <TextInput
                placeholder="Re-enter your password"
                style={[
                  {
                    height: 50,
                    borderColor: "#ccc",
                    borderWidth: 1,
                    paddingHorizontal: 10,
                    borderRadius: 10,
                    marginBottom: 10,
                    fontFamily: "Poppins-Regular",
                    position: "relative",
                  },
                  !isConfirmPasswordRequired && styles.errorInput,
                ]}
                secureTextEntry={hidePassword ? true : false}
                value={registerFormData?.confirmPassword}
                onChangeText={handleConfirmPasswordChange}
              />
              {!isConfirmPasswordRequired && (
                <Text
                  style={{
                    color: "red",
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    marginTop: 5,
                  }}
                >
                  Field required.
                </Text>
              )}
              <TouchableOpacity
                onPress={() => setHidePassword(!hidePassword)}
                style={{
                  position: "absolute",
                  right: 10,
                  top: 15,
                  width: 20,
                  height: 20,
                }}
              >
                <Image
                  source={
                    hidePassword
                      ? require("../../assets/images/hide.png")
                      : require("../../assets/images/show.png")
                  }
                  style={{
                    width: 20,
                    height: 20,
                    resizeMode: "contain",
                  }}
                />
              </TouchableOpacity>
            </View>
          </View>
          <TouchableOpacity
            style={{
              backgroundColor: "#2B6CB0",
              paddingVertical: 15,
              borderRadius: 25,
              alignItems: "center",
            }}
            onPress={handleSubmitButton}
          >
            <Text
              style={{
                color: "#fff",
                fontSize: 18,
                fontFamily: "Poppins-Medium",
              }}
            >
              Create Account
            </Text>
          </TouchableOpacity>
          <Text
            style={{
              textAlign: "center",
              marginTop: 10,
              fontSize: 11,
              fontFamily: "Poppins-Medium",
            }}
          >
            By continuing,you agree to our{" "}
            <Text style={{ color: "#007BFF", textDecorationLine: "underline" }}>
              Terms of Service
            </Text>{" "}
            and{" "}
            <Text style={{ color: "#007BFF", textDecorationLine: "underline" }}>
              Privacy Policy.
            </Text>
          </Text>
        </View>
      </View>
    </>
  );
};

export default Register;

const styles = {
  loginWrapper: {
    width: "100%",
    height: 700,
    padding: 20,
    flexDirection: "column",
  },
  inputWrapper: {
    marginBottom: 20,
  },
  googleLoginWrapper: {
    width: "90%",
    height: 150,
    backgroundColor: "#fff",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    paddingTop: 100,
  },
  errorInput: {
    borderColor: "red",
    borderWidth: 1,
    borderRadius: 10,
  },
};
