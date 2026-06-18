import { StyleSheet, Text, View, Image, TouchableOpacity } from "react-native";
import React, { useRef,useContext } from "react";
import { router } from "expo-router";
import RBSheet from "react-native-raw-bottom-sheet";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME,DARK_THEME } from "../../constants/themes";
import { useUser } from "../contexts/userContext";
import axios from "axios";

const Settings = () => {
  const {theme} = useContext(ThemeContext);
  const {user,setUser,logout} =useUser();
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  // If you're using TypeScript, prefer: const refRBSheet = useRef<RBSheet | null>(null);
  const refRBSheet = useRef();

  console.log(user);
  const handleLogOut = async () => {
  try {
    const response = await axios.post(
      "http://10.187.16.161:8000/api/accounts/logout/",
      {}, // empty body
      {
        headers: {
          Authorization: `Token ${user.token}`,
        },
      }
    );

    if (response.status === 200) {
      // optionally clear local storage
      // await AsyncStorage.removeItem("token");
      // await AsyncStorage.removeItem("user");
      await logout();

      router.replace("/authentication/login");
    }
  } catch (error) {
    console.error(error.response?.data || error.message);
  }
};
  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
      <View style={styles.logoAndSettingsTitle}>
        <Image
          source={require("../../assets/images/Pyramids.png")}
          style={{ width: 55, height: 55, resizeMode: "contain",tintColor:currentTheme.appIconColor }}
        />
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: currentTheme.text,
            // margin: "auto", // ❌ not valid in RN
            flex: 1,
            textAlign: "center", // centers the title within the row
          }}
        >
          Settings
        </Text>
      </View>

      <TouchableOpacity
        style={styles.upgradePlanWrapper}
        onPress={() => router.push("plans/plans")}
      >
        <Image source={require("../../assets/images/badge.png")} style={{ width: 55, height: 55 }} />
        <View style={{ flexDirection: "column" }}>
          <Text style={{ fontFamily: "Poppins-SemiBold", color: "white",fontSize:13 }}>
            Upgrade Plan to Unlock More!
          </Text>
          <Text style={{ fontFamily: "Poppins-Regular", color: "white", fontSize: 8.5 }}>
            Enjoy all benefits and explore more possibilities
          </Text>
        </View>
        <Image source={require("../../assets/images/right-arrow.png")} style={{ width: 20, height: 20 }} />
      </TouchableOpacity>

      <View style={styles.acutalSettingsWrapper}>
        <TouchableOpacity
          style={[styles.settingItem]}
          onPress={() => router.push("settings/personalInfo")}
        >
          <Image source={require("../../assets/images/user.png")} style={{ width: 25, height: 25,tintColor:currentTheme.iconColor }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15,color:currentTheme.text }}>Personal Info</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem} onPress={()=>{router.push('settings/billingSubscriptions')}}>
          <Image source={require("../../assets/images/crown.png")} style={{ width: 25, height: 25,tintColor:currentTheme.iconColor }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 16,color:currentTheme.text }}>Billing & Subscriptions</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>

      

        <TouchableOpacity style={styles.settingItem} onPress={() =>{router.push('currencyConverter')}}>
          <Image source={require("../../assets/images/exchange.png")} style={{ width: 25, height: 25,tintColor:currentTheme.iconColor }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 16,color:currentTheme.text }}>Live Currency Converter</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => {
            router.push("settings/paymentMethods");
          }}
        >
          <Image source={require("../../assets/images/credit-card.png")} style={{ width: 25, height: 25,tintColor:currentTheme.iconColor }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 16,color:currentTheme.text }}>Payment Methods</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => {
            router.push("settings/emergencySupport");
          }}
        >
          <Image source={require("../../assets/images/call.png")} style={{ width: 25, height: 25,tintColor:currentTheme.iconColor }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 16,color:currentTheme.text }}>Emergency Support</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem} onPress={()=>{router.push("/appAppearance")}}>
          <Image source={require("../../assets/images/eye.png")} style={{ width: 25, height: 25,tintColor:currentTheme.iconColor }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 16,color:currentTheme.text }}>App Appearance</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem} onPress={() => refRBSheet.current.open()}>
          <Image
            source={require("../../assets/images/logout.png")}
            style={{ width: 25, height: 25, tintColor: "#e24646ff" }}
          />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 16, color: "#e24646ff" }}>Logout</Text>
        </TouchableOpacity>

        <RBSheet
          ref={refRBSheet}
          // 👇 Fix: animate height on JS thread (native driver doesn't support height)
          useNativeDriver={true}
          openDuration={220}          // optional: timing
          closeDuration={180}
          customStyles={{
            // 👇 Slightly dark background behind the sheet
            wrapper: { backgroundColor: "rgba(0,0,0,0.45)" },
            container: {
              borderTopLeftRadius: 27,
              borderTopRightRadius: 27,
              padding: 16,
              backgroundColor: currentTheme.background,
              flexDirection: "column",
              height:250,
            },
            draggableIcon: { backgroundColor: "#aaa" },
          }}
        >
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 20, textAlign: "center",color:"#e24646ff",marginBottom:20 }}>
            Logout
          </Text>
          <View style={{ borderWidth:0.25,borderColor:"#c5c2c2ff",marginBottom:20, }} />
          <Text style={{ fontFamily: "Poppins-Medium", fontSize: 20, textAlign: "center", color: currentTheme.text }}>
            Are you sure you want to log out?
          </Text>
          <View style={{ flexDirection: "row", justifyContent: "space-around", marginTop: 30 }}>
            <TouchableOpacity
              style={{
                borderColor: "#D4AF37",
                borderWidth: 1,
                paddingVertical: 12,
                paddingHorizontal: 25,
                borderRadius: 20,
                alignItems: "center",
                width: "40%",
                backgroundColor: currentTheme.background,
              }}
              onPress={() => refRBSheet.current.close()}
            >
              <Text style={{ fontFamily: "Poppins-SemiBold", color: "#D4AF37" }}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={{
                backgroundColor: "#e24646ff",
                paddingVertical: 12,
                paddingHorizontal: 25,
                borderRadius: 20,
                alignItems: "center",
                width: "40%",
              }}
              onPress={handleLogOut}
            >
              <Text style={{ fontFamily: "Poppins-SemiBold", color: "white" }}>Logout</Text>
            </TouchableOpacity>
          </View>
        </RBSheet>
      </View>
    </View>
  );
};

export default Settings;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "column",
  },
  logoAndSettingsTitle: {
    flexDirection: "row",
    alignItems: "center",
    width: "82%",
    marginBottom: 15,
  },
  upgradePlanWrapper: {
    padding: 10,
    width: "100%",
    height: 100,
    backgroundColor: "#b4952fff",
    borderRadius: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },
  acutalSettingsWrapper: {
    flexDirection: "column",
    gap: 30,
  },
  settingItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 15,
    position: "relative",
  },
});
