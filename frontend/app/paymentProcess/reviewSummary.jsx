import { StyleSheet, Text, View, TouchableOpacity, Image } from "react-native";
import React, { useContext } from "react";
import { useLocalSearchParams } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import { router } from "expo-router";
import { useUser } from "../contexts/userContext";

const ReviewSummary = () => {
  const { subscription, selectedPayment } = useLocalSearchParams();
  const {user,setUser} = useUser();
  const sub = subscription ? JSON.parse(subscription) : null;
  const paymentMethod = selectedPayment ? JSON.parse(selectedPayment) : null;
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  const maskCard = (cardNumber = "") => {
    const digits = String(cardNumber).replace(/\D/g, ""); // keep only numbers
    const last4 = digits.slice(-4); // get last 4
    return "**** " + "**** " + "**** " + last4;
  };

  console.log("Subscription", sub);
  console.log("\n\n\n\n\n");
  console.log("Payment", paymentMethod);

  const handleConfirmPayment = () =>{
    setUser((prev)=>{
        return {
            ...prev,
            currentSubscription:sub,
        }
    })

    router.replace("main/settings");
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
          Review Summary
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
            {sub.name}
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
              color: currentTheme.text,
            }}
          >
            {sub.price === 0 ? "0.00 EGP " : `${sub.price} EGP`}
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
          {sub.features.map((feature, indx2) => {
            return (
              <View
                key={indx2}
                style={{
                  flexDirection: "row",
                  alignItems: "center",
                  gap: 10,
                }}
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
                  {feature}
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
          {/* {item.isCurrentPlan ? (
            <Text
              style={{
                textAlign: "center",
                fontFamily: "Poppins-Medium",
                color: "#b7b7b7ff",
              }}
            >
              Your current plan
            </Text>
          ) : (
            <TouchableOpacity
              onPress={() => {
                router.push({
                  pathname: "paymentProcess/selectPayment",
                  params: { subscription: JSON.stringify(item) },
                });
              }}
              style={{
                width: "100%",
                backgroundColor: "#D4AF37",
                paddingHorizontal: 15,
                paddingVertical: 10,
                justifyContent: "center",
                alignItems: "center",
                borderRadius: 20,
              }}
            >
              <Text style={{ fontFamily: "Poppins-Medium", color: "white" }}>
                Select Plan
              </Text>
            </TouchableOpacity>
          )} */}
        </View>
      </View>

      <View style={{ flexDirection: "column", gap: 10, marginTop: 20 }}>
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            color: currentTheme.text,
            marginBottom: 20,
          }}
        >
          Selected Payment Method
        </Text>
      </View>

      <TouchableOpacity
        style={[
          styles.countryItem,
          { backgroundColor: currentTheme.searchBackground },
        ]}
        onPress={() => {
          console.log("Payment Selected!");
        }}
      >
        <View style={{ flexDirection: "row", gap: 15, alignItems: "center" }}>
          {/* Use FastImage for better performance if needed */}
          {/* <FastImage
                                        source={{ uri: item.flags.png }}
                                        style={{ width: 80, height: 60 }}
                                        resizeMode={FastImage.resizeMode.contain}
                                      /> */}
          <Image
            source={require("../../assets/images/visa.png")}
            style={{ width: 50, height: 50 }}
          />
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              color: currentTheme.text,
              fontSize: 12,
            }}
          >
            {maskCard(paymentMethod.cardNumber)}
          </Text>
        </View>
      </TouchableOpacity>
      <TouchableOpacity
      onPress={handleConfirmPayment}
        style={{
          width: "100%",
          backgroundColor: "#D4AF37",
          paddingHorizontal: 25,
          paddingVertical: 15,
          justifyContent: "center",
          alignItems: "center",
          borderRadius: 20,
        }}
      >
        <Text style={{ fontFamily: "Poppins-SemiBold", color: "white" }}>
          Confirm Payment - {sub.price} EGP
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default ReviewSummary;

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
    backgroundColor: "#e7e7e7ff",
    borderRadius: 10,
    borderWidth: 0.1,
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
