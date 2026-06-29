import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  ScrollView,
} from "react-native";
import { router } from "expo-router";
import React, { useState, useContext, useEffect } from "react";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import { useUser } from "../contexts/userContext";
import { useNavigation } from "expo-router";
import api from "../../src/services/api";

const CurrencyConverter = () => {
  const { theme } = useContext(ThemeContext);
  const [currencyData, setCurrencyData] = useState(null);
  const { user,setUser } = useUser();
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(
          "https://open.er-api.com/v6/latest/EGP"
        );
        setCurrencyData(response.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, []);

 console.log(currencyData);

  const handleCurrencyChange = () => {
    setUser((prev)=>{
        return {
            ...prev,
            exchangeRate:currencyData.rates['USD']
        }
    })
  };
  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <View style={styles.backAndPersonalInfoTitle}>
        <TouchableOpacity onPress={() => router.replace("main/settings")}>
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
          Live Currency Converter
        </Text>
      </View>
      <ScrollView
        horizontal={false}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ flexDirection: "column", gap: 5 }}
      >
        <TouchableOpacity style={styles.countryItem} onPress={handleCurrencyChange}>
          <View style={{ flexDirection: "row", gap: 15, alignItems: "center" }}>
            {/* Use FastImage for better performance if needed */}
            {/* <FastImage
                              source={{ uri: item.flags.png }}
                              style={{ width: 80, height: 60 }}
                              resizeMode={FastImage.resizeMode.contain}
                            /> */}
            <Image
              source={require("../../assets/images/usd.png")}
              style={{ width: 20, height: 20,tintColor:currentTheme.iconColor }}
            />
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                color: currentTheme.text,
                fontSize: 17,
              }}
            >
              U.S. Dollar
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity style={styles.countryItem} >
          <View style={{ flexDirection: "row", gap: 15, alignItems: "center" }}>
            {/* Use FastImage for better performance if needed */}
            {/* <FastImage
                              source={{ uri: item.flags.png }}
                              style={{ width: 80, height: 60 }}
                              resizeMode={FastImage.resizeMode.contain}
                            /> */}
            <Image
              source={require("../..//assets/images/pound.png")}
              style={{ width: 20, height: 20,tintColor:currentTheme.iconColor }}
            />
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                color: currentTheme.text,
                fontSize: 17,
              }}
            >
              Egyptian Pound
            </Text>
          </View>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

export default CurrencyConverter;

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
    marginBottom: 35,
  },
  countryItem: {
    padding: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderColor: "#888",
    borderWidth: 0.2,
    borderRadius: 10,
    marginBottom: 20,
  },
});
