import { StyleSheet, Text, View, TouchableOpacity, Image,Switch } from "react-native";
import React, { useContext, useState, useRef } from "react";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import RBSheet from "react-native-raw-bottom-sheet";
import { isEnabled } from "react-native/Libraries/Performance/Systrace";

const AppAppearance = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const [language, setLanguage] = useState("English");
  const [isDarkModeEnabled,setIsDarkModeEnabled] = useState(true);
   const toggleSwitch = () => {
    setIsDarkModeEnabled(previousState => !previousState);
    toggleTheme();
};

  const refRBSheet = useRef();
  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <View style={styles.backAndPersonalInfoTitle}>
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 30, height: 30, tintColor: currentTheme.iconColor }}
          />
        </TouchableOpacity>
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: currentTheme.text,
            margin: "auto",
          }}
        >
          App Appearance
        </Text>
      </View>

      <View style={styles.themeAndLanguageWrapper}>
        <TouchableOpacity
          style={styles.appPreferenceItem}
          onPress={() => refRBSheet.current.open()}
        >
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              fontSize: 17,
              color: currentTheme.text,
            }}
          >
            Theme
          </Text>

          <View
            style={{ flexDirection: "row", gap: 20, justifyContent: "center" }}
          >
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 17,
                color: currentTheme.text,
              }}
            >
              {theme}
            </Text>
            <Image
              source={require("../../assets/images/right-arrow.png")}
              style={{
                width: 25,
                height: 25,
                tintColor: currentTheme.iconColor,
              }}
            />
          </View>
        </TouchableOpacity>

        <RBSheet
          ref={refRBSheet}
          // 👇 Fix: animate height on JS thread (native driver doesn't support height)
          useNativeDriver={true}
          openDuration={220} // optional: timing
          closeDuration={180}
          customStyles={{
            // 👇 Slightly dark background behind the sheet
            wrapper: { backgroundColor: "rgba(0,0,0,0.45)" },
            container: {
              borderTopLeftRadius: 27,
              borderTopRightRadius: 27,
              padding: 22,
              backgroundColor: currentTheme.background,
              flexDirection: "column",
              height:350
            },
            draggableIcon: { backgroundColor: "#aaa" },
          }}
        >
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 20,
              textAlign: "center",
              color: currentTheme.text,
              marginBottom:20,
            }}
          >
            Choose Theme
          </Text>
          <View
            style={{
              borderWidth: 0.25,
              borderColor: "#c5c2c2ff",
              marginBottom: 20,
            }}
          />
           <View style={{alignItems:"center",flexDirection:"row",justifyContent:"space-between"}}>
          <Text style={{color:currentTheme.text,fontFamily:"Poppins-Medium"}}>
            {theme} Mode
          </Text>
           <Switch
          trackColor={{false: '#767577', true: '#81b0ff'}}
          thumbColor={isDarkModeEnabled ? 'silver' : '#f4f3f4'}
          ios_backgroundColor="#3e3e3e"
          value = {isDarkModeEnabled}
          onValueChange={toggleSwitch}
        />
        </View>
        </RBSheet>
        <TouchableOpacity style={styles.appPreferenceItem}>
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              fontSize: 17,
              color: currentTheme.text,
            }}
          >
            App Language
          </Text>

          <View
            style={{ flexDirection: "row", gap: 20, justifyContent: "center" }}
          >
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 17,
                color: currentTheme.text,
              }}
            >
              {language}
            </Text>
            <Image
              source={require("../../assets/images/right-arrow.png")}
              style={{
                width: 25,
                height: 25,
                tintColor: currentTheme.iconColor,
              }}
            />
          </View>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default AppAppearance;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "column",
    // backgroundColor:"#fff",
  },
  backAndPersonalInfoTitle: {
    flexDirection: "row",
    alignItems: "center",
    width: "90%",
    marginBottom: 30,
  },
  themeAndLanguageWrapper: {
    flexDirection: "column",
    gap: 35,
  },
  appPreferenceItem: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
});
