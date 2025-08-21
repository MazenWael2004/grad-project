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

const Login = () => {
  const [hidePassword, setHidePassword] = useState(true);
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
            style={{
              height: 50,
              borderColor: "#ccc",
              borderWidth: 1,
              paddingHorizontal: 10,
              borderRadius: 5,
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
              marginBottom: 10,
            }}
          >
            Password
          </Text>
          <View>
            <TextInput
              placeholder="Enter your password"
              style={{
                height: 50,
                borderColor: "#ccc",
                borderWidth: 1,
                paddingHorizontal: 10,
                borderRadius: 5,
                fontFamily: "Poppins-Regular",
                position: "relative",
              }}
              secureTextEntry={hidePassword?true:false}
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
                source={hidePassword?require("../../assets/images/hide.png"):require("../../assets/images/show.png")}
                style={{
                  width: 20,
                  height: 20,
                  resizeMode: "contain",
                }}
              />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
};

export default Login;

const styles = {
  loginWrapper: {
    width: "100%",
    height: 400,
    padding: 20,
    flexDirection: "column",
  },
  inputWrapper: {
    marginBottom: 20,
  },
};
