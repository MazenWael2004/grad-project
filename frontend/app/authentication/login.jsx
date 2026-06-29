import {
  StyleSheet,
  Text,
  View,
  TextInput,
  Image,
  TouchableOpacity,
} from "react-native";
import React, { use, useState } from "react";
import { hide } from "expo-splash-screen";
import {useRouter} from "expo-router";
import { Alert } from "react-native";
import api from "../../src/services/api";
import { useUser } from "../contexts/userContext";
import Constants from "expo-constants";
import AsyncStorage from "@react-native-async-storage/async-storage";
const { API_BASE_URL } = Constants.expoConfig.extra;

const Login = () => {
  const [email, setEmail] = useState("");
  const { user, setUser } = useUser();
  const [password, setPassword] = useState("");
  const [hidePassword, setHidePassword] = useState(true);
  const [isPasswordCorrect,setIsPasswordCorrect] = useState(true);
  const router = useRouter();

  const handleEmailChange = (text)=>{
    setEmail(text);
    console.log("Login Form Email: "+text);
    
  }

  const handlePasswordChange = (text)=>{
    setPassword(text);
    console.log("Login Form Password:"+text);
  }

  const handleLogin = async () => {
   if(!email || !password){
    Alert.alert("Please Input Required Fields.")
    return;
   } 
   // Email Validation
   const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
   if(!emailRegex.test(email)){
     Alert.alert("Invalid Email")
     return;
   } 

  try {
    const response = await api.post("/api/accounts/login/", {
     email,
     password,
    });

    if (response.status === 200) {
      const user = response.data.user;
      // const token = response.data.token;

      const access = response.data.access;
      const refresh = response.data.refresh;

      await AsyncStorage.setItem("access", access);
      await AsyncStorage.setItem("refresh", refresh);
      await AsyncStorage.setItem("user", JSON.stringify(user));


      Alert.alert("Success", "Account Successfully Logged In");
      // Setting user context after registering...
      setUser({
       userId:user.id,
       first_name:user.first_name,
       last_name:user.last_name,
       email:user.email,
       country:user.country,
       subscriptionID:1,
       paymentMethods: [],
       phoneNumber:user.phone_number,
       access,
       refresh,
      })
      router.replace("/main/");
    }
  } catch (error) {
    console.error(error.response?.data || error.message);
    Alert.alert("Error", "Registration failed. Try again.");
  }
  
};



  return (
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
        Login
      </Text>
      <View style={styles.loginWrapper}>
        <View style={styles.inputWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              fontSize: 16,
              color: "#333",
              marginBottom: 10,
            }}
          >
            E-mail
          </Text>
          <TextInput
            
            placeholder="Enter your email"
            onChangeText={handleEmailChange}
            style={{
              height: 50,
              borderColor: "#ccc",
              borderWidth: 1,
              paddingHorizontal: 10,
              borderRadius: 10,
              fontFamily: "Poppins-Regular",
            }}
          />
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
          </Text>
          <View>
            <TextInput
              placeholder="Enter your password"
              onChangeText={handlePasswordChange}
              style={
                [{
                height: 50,
                borderColor: "#ccc",
                borderWidth: 1,
                paddingHorizontal: 10,
                borderRadius: 10,
                marginBottom: 10,
                fontFamily: "Poppins-Regular",
                position: "relative",
              },
              !isPasswordCorrect && styles.errorInput
              
           ] }
              secureTextEntry={hidePassword ? true : false}
            />
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
           {!isPasswordCorrect && (
          <Text style={{color:"red",fontFamily:"Poppins-Medium",fontSize:13}}>Incorrect Password. Please check your password.</Text>
        )}
        </View>
       
        <TouchableOpacity onPress={() => console.log("Forgot Password")}>
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              fontSize: 16,
              color: "#007BFF",
              textAlign: "right",
              marginBottom: 20,
            }}
          >
            Forgot Password?
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={{
            backgroundColor: "#2B6CB0",
            paddingVertical: 15,
            borderRadius: 25,
            alignItems: "center",
          }}
          onPress={handleLogin}
        >
          <Text
            style={{
              color: "#fff",
              fontSize: 18,
              fontFamily: "Poppins-Medium",
            }}
          >
            Login
          </Text>
        </TouchableOpacity>
        <View>
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              fontSize: 14,
              color: "#333",
              textAlign: "center",
              marginTop: 10,
            }}
          >
            Don&apos;t have an account?{" "}
            <Text
              style={{
                color: "#007BFF",
                textDecorationLine: "underline",
              }}
              onPress={() => router.push("authentication/register")}
            >
              Sign Up
            </Text>
          </Text>
        </View>
      </View>
      {/* <View style={styles.googleLoginWrapper}>
        <Text
          style={{
            color: "rgba(102, 98, 98, 1)",
            fontFamily: "Poppins-Medium",
            marginBottom: 10,
          }}
        >
          or login with
        </Text>
        <TouchableOpacity
          style={{
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center",
            borderWidth: 1,
            borderColor: "#ccc",
            paddingVertical: 10,
            paddingHorizontal: 20,
            borderRadius: 25,
            backgroundColor: "#fff",
            width:"90%"
          }}
          onPress={() => console.log("Google Login")}
        >
          <Image
            source={require("../../assets/images/google.png")}
            style={{
              width: 20,
              height: 20,
              marginRight: 10,
              resizeMode: "contain",
            }}
          />
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              fontSize: 16,
              color: "#333",
            }}
          >
            Continue with Google
          </Text>
        </TouchableOpacity>
      </View> */}
    </View>
  );
};

export default Login;

const styles = {
  loginWrapper: {
    width: "100%",
    height: 500,
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
  errorInput:{
    borderColor: "red",
    borderWidth: 1,
    borderRadius: 10,
  }
};
