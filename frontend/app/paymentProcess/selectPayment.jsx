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
import { useLocalSearchParams } from "expo-router";

const SelectPayment = () => {
  const {subscription} = useLocalSearchParams();
  const [isPaymentMethodExists, setIsPaymentMethodExists] = useState(false);
  const nav  = useNavigation();
  const {user,setUser} = useUser();
  const { theme } = useContext(ThemeContext);
  const [selectedPaymentMethod,setSelectedPaymentMethod] = useState(null);
  const [cardTypeImage,setCardTypeImage] = useState(null);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  useEffect(()=>{
    if(user.paymentMethods.length === 0){
      setIsPaymentMethodExists(false);
    }
    else{
      setIsPaymentMethodExists(true);
    }
    console.log(JSON.stringify(user.paymentMethods, null,2));

  },[user.paymentMethods]);

 const sub = subscription ? JSON.parse(subscription) : null;

  console.log(sub); // full object you passed


  const maskCard = (cardNumber = "") => {
  const digits = String(cardNumber).replace(/\D/g, ""); // keep only numbers
  const last4 = digits.slice(-4); // get last 4
  return "**** "+"**** "+"**** "+last4;
};


const handlePaymentSelection = (item)=>{
 setSelectedPaymentMethod(item);
 console.log("Payment Selected!",item);
 router.push({
    pathname: "paymentProcess/reviewSummary",
    params: { subscription: JSON.stringify(sub),selectedPayment:JSON.stringify(item) }, // 👈 better: stringify object
  });

} 

 

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
          Select Payment Method
        </Text>
      </View>
      {!isPaymentMethodExists ? (
        <View style={styles.noPaymentAddedContainer}>
          <Image
            source={require("../../assets/images/payment-method.png")}
            style={{
              width: 160,
              height: 160,
              tintColor: currentTheme.description,
            }}
          />
          <Text
            style={{
              fontSize: 26,
              fontFamily: "Poppins-SemiBold",
              textAlign: "center",
              color: currentTheme.text,
            }}
          >
            No Payment Method Added.
          </Text>

          <TouchableOpacity
            style={{
              backgroundColor: "#D4AF37",
              justifyContent: "center",
              alignItems: "center",
              padding: 20,
              borderRadius: 15,
            }}
            onPress={() => {
              router.push("addPaymentMethod");
            }}
          >
            <Text
              style={{
                fontFamily: "Poppins-SemiBold",
                color: "white",
                width: "100%",
              }}
            >
              Add Payment Method
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView
          horizontal={false}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ flexDirection: "column", gap: "15" }}
        >

{user.paymentMethods.map((item,indx) =>{
  return (
    <TouchableOpacity
    key={indx}
            style={[styles.countryItem,{backgroundColor:currentTheme.searchBackground}]}
            onPress={() => handlePaymentSelection(item)  }
          >
            <View
              style={{ flexDirection: "row", gap: 15, alignItems: "center" }}
            >
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
                  fontSize:12,
                }}
              >
                {maskCard(item.cardNumber)}
                </Text>
            </View>
          </TouchableOpacity>

  )
})}

          
        </ScrollView>
        
      )}
    </View>
  );
};

export default SelectPayment;

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
    marginBottom:35,
  },
  noPaymentAddedContainer: {
    height: "85%",
    flexDirection: "column",
    gap: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  countryItem: {
    padding: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderColor: "#888",
    borderWidth: 0.2,
    borderRadius: 10,
    marginBottom:20,
  },
});
