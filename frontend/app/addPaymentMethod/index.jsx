import React, { useState,useContext } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  TextInput,
} from "react-native";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME,DARK_THEME } from "../../constants/themes";
import { useUser } from "../contexts/userContext";
import { useNavigation } from "expo-router";



const AddPaymentMethod = () => {
  const {user,setUser} = useUser();
  const nav = useNavigation();
  const [cardNumber, setCardNumber] = useState("");
  const [accountHolderName, setAccountHolderName] = useState("");
  const [cardType,setCardType] = useState("");
  const [isCardNumberValidated,setIsCardNumberValidated] = useState(true);
  const [expiryDate,setExpiryDate] = useState({
    expiryMonth: "",
    expiryYear: "",
  });
  // const [expMonth, setExpMonth] = useState("");
  // const [expYear, setExpYear] = useState("");
  const [cvv, setCvv] = useState("");
  const {theme} = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  const handleReset = () => {
    setCardNumber("");
    setAccountHolderName("");
    // setExpMonth("");
    // setExpYear("");
    setCvv("");
    setIsCardNumberValidated(true);
  };

  const handleCardNumberChange = (text) =>{
    // console.log(text.length);
    // if(text.length % 4 === 0){
    //   text+=" ";
    // }

    if(text[0]=== '4'){
      console.log("Visa Card");
      setCardType("Visa");
    }
    else if(text[0] === '5' || text[0] === '2'){
      console.log("MasterCard Card");
      setCardType("MasterCard");
    }
    setCardNumber(text);
    console.log("Card Number: "+text);
  }

  const handleAccountHolderName = (text) =>{
    setAccountHolderName(text);
    console.log("Account Holder Name: "+text);
  }

  const handleExpiryMonthChange  = (text) =>{
    setExpiryDate((prev)=>{
      return {
        ...prev,
        expiryMonth:text
      }
    })

    console.log("Expiry Month:"+text)
  }

  const handleExpiryYearChange  = (text) =>{
    setExpiryDate((prev)=>{
      return {
        ...prev,
        expiryYear:text
      }
    })

    console.log("Expiry Year:"+text)
  }

  const handleCVVChange = (text) =>{
    setCvv(text);
    console.log("CVV: "+text);
  }

  const isValidate  = () =>{
    // Validate Card Number
    if(cardNumber[0] === '4'){
      console.log("Card Number is a Visa Card!");
      setIsCardNumberValidated(true);
      return true;
    }
    else{
      console.log("Invaild Card Number!");
      setIsCardNumberValidated(false);
      return false;
    }
  }

  const handleSaveMethod = ()=>{
    if(isValidate()){
    setUser((prev)=>{
      return {
        ...prev,
        paymentMethods: [
          ...prev.paymentMethods,
          {
             id: prev.paymentMethods.length + 1,
             cardHolderName: accountHolderName,
             cardNumber,
             expiryDate,
             cardType,
             CVV: cvv
          }
        ]
      }
    })
    router.push("settings/paymentMethods");
  }
  else{
    console.log("Validation Error!");
  }

    // console.log(user);
    
  }

  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.iconHitbox}
        >
          <Image
            source={require("../../assets/images/back.png")}
            style={[styles.backIcon,{tintColor:currentTheme.iconColor}]}
            resizeMode="contain"
          />
        </TouchableOpacity>

        <Text style={[styles.title,{color:currentTheme.text}]}>Add New Payment</Text>

        <TouchableOpacity onPress={handleReset}>
          <Text style={styles.resetText}>RESET</Text>
        </TouchableOpacity>
      </View>

      {/* Form */}
      <View style={styles.form}>
        {/* Card Number */}
        <View style={styles.inputWrapper}>
          <Text style={[styles.label,{color:currentTheme.text}]}>Card Number</Text>
          <TextInput
            value={cardNumber}
            onChangeText={handleCardNumberChange}
            placeholder="Ex: 2640 1234 5678 9012"
            placeholderTextColor="#6b6b6b"
            style={[styles.input,{backgroundColor:currentTheme.searchBackground,color:currentTheme.text},!isCardNumberValidated && styles.errorInput]}
            keyboardType="number-pad"
            maxLength={16} // 16 digits + 3 spaces if you later format xxxx xxxx xxxx xxxx
          />
        </View>

        {/* Account Holder Name */}
        <View style={styles.inputWrapper}>
          <Text style={[styles.label,{color:currentTheme.text}]}>Account Holder Name</Text>
          <TextInput
            value={accountHolderName}
            onChangeText={handleAccountHolderName}
            placeholder="John Doe"
            placeholderTextColor="#6b6b6b"
            style={[styles.input,{backgroundColor:currentTheme.searchBackground,color:currentTheme.text}]}
            autoCapitalize="words"
            autoCorrect={false}
          />
        </View>

        {/* Expiry + CVV in two columns */}
        <View style={styles.twoCols}>
          {/* Expiry */}
          <View style={styles.col}>
            <Text style={[styles.label,{color:currentTheme.text}]}>Expiry Date</Text>
            <View style={[styles.expiryField,{backgroundColor:currentTheme.searchBackground}]}>
              <TextInput
                value={expiryDate.expiryMonth}
                onChangeText={handleExpiryMonthChange}
                placeholder="MM"
                placeholderTextColor="#6b6b6b"
                style={[styles.expiryInput, { width: 40 },{color:currentTheme.text}]}
                keyboardType="number-pad"
                maxLength={2}
              />
              <Text style={styles.slash}>/</Text>
              <TextInput
                value={expiryDate.expiryYear}
                onChangeText={handleExpiryYearChange}
                placeholder="YY"
                placeholderTextColor="#6b6b6b"
                style={[styles.expiryInput, { width: 46 },{color:currentTheme.text}]}
                keyboardType="number-pad"
                maxLength={2}
              />
            </View>
          </View>

          {/* CVV */}
          <View style={styles.colRight}>
            <Text style={[styles.label,{color:currentTheme.text}]}>CVV</Text>
            <TextInput
              value={cvv}
              onChangeText={setCvv}
              placeholder="123"
              placeholderTextColor="#6b6b6b"
              style={[styles.input,{backgroundColor:currentTheme.searchBackground},{color:currentTheme.text}]}
              keyboardType="number-pad"
              secureTextEntry
              maxLength={3}
            />
          </View>
        </View>
      </View>
      <View
        style={{
          borderWidth: 0.25,
          borderColor: "#bababaff",
          width: "100%",
          marginBottom: 20,
        }}
      />
      <View style={styles.supportedPaymentsWrapper}>
        <Text style={{ fontSize: 16, fontFamily: "Poppins-Medium",color:currentTheme.text }}>
          Supported Payments:
        </Text>
        <View
          style={{ flexDirection: "row", alignItems: "center", gap: 20 }}
        >
          <Image
            source={require("../../assets/images/round.png")}
            style={{ width: 60, height: 60 }}
            resizeMode="contain"
          />

          <Image
            source={require("../../assets/images/visa.png")}
            style={{ width: 60, height: 60 }}
            resizeMode="contain"
          />

           <Image
            source={require("../../assets/images/paypal.png")}
            style={{ width: 60, height: 60 }}
            resizeMode="contain"
          />
        </View>
      </View>
      <TouchableOpacity
        style={{
          backgroundColor: "#D4AF37",
          paddingVertical: 16,
          borderRadius: 10,
          alignItems: "center",
          position: "absolute",
          bottom:1,
          left: 20,
          right: 20,
          marginBottom: 20,
        }}
        onPress={
          // Handle form submission here
          handleSaveMethod
        }
      >
        <Text
          style={{
            color: "#FFFFFF",
            fontFamily: "Poppins-SemiBold",
            fontSize: 16,
            textTransform: "uppercase",
            letterSpacing: 1.5,
          }}
        >
          Save
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default AddPaymentMethod;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 70,
    // backgroundColor: "#FFFFFF",
    position: "relative",
  },

  /* Header */
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    width: "100%",
    marginBottom: 24,
  },
  iconHitbox: {
    padding: 4,
  },
  backIcon: {
    width: 30,
    height: 30,
  },
  title: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 20,
    // color: "#000000",
  },
  resetText: {
    fontFamily: "Poppins-Regular",
    fontSize: 16,
    color: "#e24646ff",
    textTransform: "uppercase",
    letterSpacing: 1.5,
  },

  /* Form */
  form: {
    width: "100%",
    // Removed fixed height to avoid clipping on smaller screens
    marginBottom: 34,
  },
  inputWrapper: {
    marginBottom: 16,
  },
  label: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 14,
    // color: "#222222",
    marginBottom: 6,
  },
  input: {
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 10,
    // backgroundColor: "#ECE8E8",
    fontFamily: "Poppins-SemiBold",
    fontSize: 16,
    color: "#000000",
  },

  /* Two columns for Expiry + CVV */
  twoCols: {
    flexDirection: "row",
    width: "100%",
    alignItems: "flex-start",
  },
  col: {
    flex: 1,
  },
  colRight: {
    flex: 1,
    marginLeft: 12,
  },

  /* Expiry composite field */
  expiryField: {
    // backgroundColor: "#ECE8E8",
    borderRadius: 10,
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    height: 55,
  },
  expiryInput: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 16,
    color: "#000000",
    textAlign: "center",
    paddingVertical: 10,
  },
  slash: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 16,
    color: "#000000",
    marginHorizontal: 6,
  },
  supportedPaymentsWrapper: {
    flexDirection: "column",
    gap: 10,
  },
    errorInput: {
    borderColor: "#e24646ff",
    borderWidth: 1,
    borderRadius: 10,
  },
});
