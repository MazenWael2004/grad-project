import { StyleSheet, Text, View, Image, TouchableOpacity } from "react-native";
import React, { useRef } from "react";
import { router } from "expo-router";
import RBSheet from "react-native-raw-bottom-sheet";

const Settings = () => {
  // If you're using TypeScript, prefer: const refRBSheet = useRef<RBSheet | null>(null);
  const refRBSheet = useRef();

  return (
    <View style={styles.container}>
      <View style={styles.logoAndSettingsTitle}>
        <Image
          source={require("../../assets/images/Pyramids.png")}
          style={{ width: 55, height: 55, resizeMode: "contain" }}
        />
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: "#000000ff",
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
          <Text style={{ fontFamily: "Poppins-SemiBold", color: "white" }}>
            Upgrade Plan to Unlock More!
          </Text>
          <Text style={{ fontFamily: "Poppins-Regular", color: "white", fontSize: 8 }}>
            Enjoy all benefits and explore more possibilities
          </Text>
        </View>
        <Image source={require("../../assets/images/right-arrow.png")} style={{ width: 20, height: 20 }} />
      </TouchableOpacity>

      <View style={styles.acutalSettingsWrapper}>
        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => router.push("settings/personalInfo")}
        >
          <Image source={require("../../assets/images/user.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>Personal Info</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <Image source={require("../../assets/images/crown.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>Billing & Subscriptions</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <Image source={require("../../assets/images/security.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>Account & Security</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <Image source={require("../../assets/images/exchange.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>Live Currency Converter</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => {
            router.push("settings/paymentMethods");
          }}
        >
          <Image source={require("../../assets/images/credit-card.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>Payment Methods</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={() => {
            router.push("settings/emergencySupport");
          }}
        >
          <Image source={require("../../assets/images/call.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>Emergency Support</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <Image source={require("../../assets/images/eye.png")} style={{ width: 25, height: 25 }} />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15 }}>App Appearance</Text>
          <Image
            source={require("../../assets/images/right-arrow.png")}
            style={{ width: 25, height: 25, position: "absolute", right: 1 }}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem} onPress={() => refRBSheet.current.open()}>
          <Image
            source={require("../../assets/images/logout.png")}
            style={{ width: 25, height: 25, tintColor: "red" }}
          />
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 15, color: "red" }}>Logout</Text>
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
              backgroundColor: "#fff",
              flexDirection: "column",
            },
            draggableIcon: { backgroundColor: "#aaa" },
          }}
        >
          <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 20, textAlign: "center",color:"red" }}>
            Logout
          </Text>
          <View style={{ borderWidth:0.25,borderColor:"#c5c2c2ff",marginBottom:20, }} />
          <Text style={{ fontFamily: "Poppins-Medium", fontSize: 20, textAlign: "center", color: "#000000ff" }}>
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
                backgroundColor: "#ffffffff",
              }}
              onPress={() => refRBSheet.current.close()}
            >
              <Text style={{ fontFamily: "Poppins-SemiBold", color: "#D4AF37" }}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={{
                backgroundColor: "#cd2121ff",
                paddingVertical: 12,
                paddingHorizontal: 25,
                borderRadius: 20,
                alignItems: "center",
                width: "40%",
              }}
              onPress={() => {
                refRBSheet.current.close();
                console.log("Logged out");
                // Add actual logout logic here
                // router.replace("/");
              }}
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
    backgroundColor: "#D4AF37",
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
