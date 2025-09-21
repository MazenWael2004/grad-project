import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  TextInput,
} from "react-native";
import { router } from "expo-router";

const AddPaymentMethod = () => {
  const [cardNumber, setCardNumber] = useState("");
  const [accountHolderName, setAccountHolderName] = useState("");
  const [expMonth, setExpMonth] = useState("");
  const [expYear, setExpYear] = useState("");
  const [cvv, setCvv] = useState("");

  const handleReset = () => {
    setCardNumber("");
    setAccountHolderName("");
    setExpMonth("");
    setExpYear("");
    setCvv("");
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.iconHitbox}
        >
          <Image
            source={require("../../assets/images/back.png")}
            style={styles.backIcon}
            resizeMode="contain"
          />
        </TouchableOpacity>

        <Text style={styles.title}>Add New Payment</Text>

        <TouchableOpacity onPress={handleReset}>
          <Text style={styles.resetText}>RESET</Text>
        </TouchableOpacity>
      </View>

      {/* Form */}
      <View style={styles.form}>
        {/* Card Number */}
        <View style={styles.inputWrapper}>
          <Text style={styles.label}>Card Number</Text>
          <TextInput
            value={cardNumber}
            onChangeText={setCardNumber}
            placeholder="Ex: 2640 1234 5678 9012"
            placeholderTextColor="#6b6b6b"
            style={styles.input}
            keyboardType="number-pad"
            maxLength={19} // 16 digits + 3 spaces if you later format xxxx xxxx xxxx xxxx
          />
        </View>

        {/* Account Holder Name */}
        <View style={styles.inputWrapper}>
          <Text style={styles.label}>Account Holder Name</Text>
          <TextInput
            value={accountHolderName}
            onChangeText={setAccountHolderName}
            placeholder="John Doe"
            placeholderTextColor="#6b6b6b"
            style={styles.input}
            autoCapitalize="words"
            autoCorrect={false}
          />
        </View>

        {/* Expiry + CVV in two columns */}
        <View style={styles.twoCols}>
          {/* Expiry */}
          <View style={styles.col}>
            <Text style={styles.label}>Expiry Date</Text>
            <View style={styles.expiryField}>
              <TextInput
                value={expMonth}
                onChangeText={setExpMonth}
                placeholder="MM"
                placeholderTextColor="#6b6b6b"
                style={[styles.expiryInput, { width: 40 }]}
                keyboardType="number-pad"
                maxLength={2}
              />
              <Text style={styles.slash}>/</Text>
              <TextInput
                value={expYear}
                onChangeText={setExpYear}
                placeholder="YY"
                placeholderTextColor="#6b6b6b"
                style={[styles.expiryInput, { width: 46 }]}
                keyboardType="number-pad"
                maxLength={2}
              />
            </View>
          </View>

          {/* CVV */}
          <View style={styles.colRight}>
            <Text style={styles.label}>CVV</Text>
            <TextInput
              value={cvv}
              onChangeText={setCvv}
              placeholder="123"
              placeholderTextColor="#6b6b6b"
              style={styles.input}
              keyboardType="number-pad"
              secureTextEntry
              maxLength={4}
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
        <Text style={{ fontSize: 16, fontFamily: "Poppins-Medium" }}>
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
        onPress={() => {
          // Handle form submission here
          console.log("Form submitted");
        }}
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
    backgroundColor: "#FFFFFF",
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
    color: "#000000",
  },
  resetText: {
    fontFamily: "Poppins-Regular",
    fontSize: 16,
    color: "#d91212",
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
    color: "#222222",
    marginBottom: 6,
  },
  input: {
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 10,
    backgroundColor: "#ECE8E8",
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
    backgroundColor: "#ECE8E8",
    borderRadius: 10,
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    height: 50,
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
});
