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

const Register = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [hidePassword, setHidePassword] = useState(true);
  const [isPasswordCorrect,setIsPasswordCorrect] = useState(true);
  const router = useRouter();
  return (
    <>
    <TouchableOpacity style={{position:"absolute",top:50,left:20,zIndex:1,backgroundColor:"#e6e1e1ff",borderRadius:20,padding:5}} onPress={() => router.back()}>
        <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 30, height: 30}}
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
  <View style={{ flex: 1,marginBottom:10,}}>
    <Text
      style={{
        fontFamily: "Poppins-Medium",
        fontSize: 16,
        color: "#333",
        marginBottom: 10,
      }}
    >
      First Name
      <Text style={{color:"red"}}> *</Text>
    </Text>
    <TextInput
      placeholder="John"
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
      <Text style={{color:"red"}}> *</Text>
    </Text>
    <TextInput
      placeholder="Doe"
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
            <Text style={{color:"red"}}> *</Text>
          </Text>
          <View>
            <TextInput
              placeholder="Enter your email"
              style={
                [{
                height: 50,
                borderColor: "#ccc",
                borderWidth: 1,
                paddingHorizontal: 10,
                borderRadius: 10,
                marginBottom: 2,
                fontFamily: "Poppins-Regular",
                position: "relative",
              },

              
           ] }
              
            />
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
            <Text style={{color:"red"}}> *</Text>
          </Text>
          <View>
            <TextInput
              placeholder="Enter your Country"
              style={
                [{
                height: 50,
                borderColor: "#ccc",
                borderWidth: 1,
                paddingHorizontal: 10,
                borderRadius: 10,
                marginBottom: 2,
                fontFamily: "Poppins-Regular",
                position: "relative",
              },

              
           ] }
              
            />
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
                    <Text style={{color:"red"}}> *</Text>
                  </Text>
                  <View>
                    <TextInput
                      placeholder="Enter your password"
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
                    <Text style={{color:"red"}}> *</Text>
                  </Text>
                  <View>
                    <TextInput
                      placeholder="Re-enter your password"
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
                </View>
        <TouchableOpacity
          style={{
            backgroundColor: "#2B6CB0",
            paddingVertical: 15,
            borderRadius: 25,
            alignItems: "center",
          }}
          onPress={() => {
            router.push("personalization/travelPreferences");
          }}
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
        <Text style={{textAlign:"center",marginTop:10,fontSize:11,fontFamily:"Poppins-Medium"}}>
            By continuing,you agree to our <Text style={{color:"#007BFF",textDecorationLine:"underline"}}>Terms of Service</Text> and <Text style={{color:"#007BFF",textDecorationLine:"underline"}}>Privacy Policy.</Text>
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
    height: 600,
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
