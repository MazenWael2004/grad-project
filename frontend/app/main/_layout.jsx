import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { StyleSheet } from "react-native";
import { ThemeContext } from "../../theme/ThemeContext";
import { useContext } from "react";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import { Image } from "react-native";

export default function Layout() {
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: true,
        tabBarActiveTintColor: "#b29227ff", // gold-like active color
        tabBarInactiveTintColor: "#9f9e9eff", // muted gray
        tabBarLabelStyle: {
          fontFamily: "Poppins-Medium",
          fontSize: 12,
          marginBottom: 5,
        },
        tabBarStyle: {
          borderTopLeftRadius: 20,
          borderTopRightRadius: 20,
          backgroundColor: currentTheme.background,
          position: "absolute",
          shadowColor: "#000",
          shadowOpacity: 0.1,
          shadowRadius: 10,
          elevation: 5,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ focused, color, size }) => (
            <Image
              source={
                require("../../assets/images/tent.png")
              }
              style={{
                width: 28,
                height: 28,
                tintColor: focused ? "#b29227ff" : "#9f9e9eff", // تغيير اللون حسب الحالة
              }}
            />
          ),
        }}
      />

      <Tabs.Screen
        name="saved"
        options={{
          title: "Saved",
          tabBarIcon: ({ color, size,focused }) => (
           <Image
              source={
                focused?require("../../assets/images/saved-egypt-outlined.png"):require("../../assets/images/saved-egypt.png")
              }
              style={{
                width: 28,
                height: 28,
                tintColor: focused ? "#b29227ff" : "#9f9e9eff", // تغيير اللون حسب الحالة
              }}
            />
          ),
        }}
      />

      <Tabs.Screen
        name="myTrips"
        options={{
          title: "My Trips",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="location-outline" size={size} color={color} />
          ),
        }}
      />

      <Tabs.Screen
        name="settings"
        options={{
          title: "Settings",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings-outline" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  logoWrapper: {
    top: -20,
    backgroundColor: "white",
    borderRadius: 50,
    padding: 10,
    elevation: 5,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 5,
  },
  logo: {
    width: 50,
    height: 50,
  },
});
