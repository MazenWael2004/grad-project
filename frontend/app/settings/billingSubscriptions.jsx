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
import subscriptions from "../../constants/subscriptions";

const Billing = () => {
  const { theme } = useContext(ThemeContext);
  const { user } = useUser();
  const subscription_id = user.subscriptionID;
  const subscription = subscriptions.find((item)=>item.id === subscription_id);

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
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
          Billing & Subscriptions
        </Text>
      </View>
      <View
        style={[
          styles.subscriptionWrapper,
          { backgroundColor: currentTheme.searchBackground },
        ]}
      >
        <View
          style={{
            width: "100%",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              marginTop: 19,
              color: currentTheme.text,
            }}
          >
            {subscription.name}
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
              color: currentTheme.text,
            }}
          >
            {subscription.price === 0
              ? "Free"
              : `${subscription.price}/month`}
          </Text>
        </View>

        <View
          style={{
            borderBottomColor: currentTheme.borderBottomColor,
            borderBottomWidth: 1,
            width: "100%",
            height: 10,
          }}
        />

        <View style={{ flexDirection: "column", gap: 10, padding: 25 }}>
          {subscription.features.map((item, indx) => {
            return (
              <View
                key={indx}
                style={{ flexDirection: "row", alignItems: "center", gap: 10 }}
              >
                <Image
                  source={require("../../assets/images/check.png")}
                  style={{
                    width: 15,
                    height: 15,
                    tintColor: currentTheme.iconColor,
                  }}
                />

                <Text
                  style={{
                    fontFamily: "Poppins-Medium",
                    fontSize: 13,
                    color: currentTheme.text,
                  }}
                >
                  {item}
                </Text>
              </View>
            );
          })}

          <View
            style={{
              borderBottomColor: currentTheme.borderBottomColor,
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
              marginBottom: 10,
            }}
          />

          <Text
            style={{
              textAlign: "center",
              fontFamily: "Poppins-Medium",
              color: "#b7b7b7ff",
            }}
          >
            Your current plan
          </Text>
        </View>
      </View>
    </View>
  );
};

export default Billing;

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
  subscriptionWrapper: {
    position: "relative",
    width: "100%",
    height: "auto",
    // backgroundColor: "#e7e7e7ff",
    borderRadius: 10,
    borderWidth: 0.1,
  },
});
