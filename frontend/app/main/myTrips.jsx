import { StyleSheet, Text, View, Image,TouchableOpacity } from "react-native";
import React, { useState } from "react";

const MyTrips = () => {
  const [isEmpty, setIsEmpty] = useState(true);
  return (
    <View style={styles.container}>
      <View style={styles.logoandTitleWrapper}>
        <Image
          source={require("../../assets/images/Pyramids.png")}
          style={{ width: 55, height: 55, resizeMode: "contain" }}
        />
        <Text
          style={{
            fontFamily: "Poppins-ExtraBold",
            fontSize: 30,
            color: "#D2691E",
            margin: "auto",
          }}
        >
          Historai
        </Text>
      </View>
      {isEmpty ? (
       <View style={styles.NoTripSavedWrapper}>
        <Image
          source={require("../../assets/images/gps.png")}
          style={{ width: 100, height: 100, marginBottom: 50 }}
        />
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 29,
            color: "black",
            marginBottom: 15,
          }}
        >
          Empty
        </Text>
        <Text
          style={{ fontFamily: "Poppins-Regular", fontSize: 13, color: "#666",textAlign:"center",marginBottom:10 }}
        >
          Let our AI create personalized trip plans just for you. Start planning now!
        </Text>
        {/* <TouchableOpacity style={{borderRadius:25,backgroundColor:"#D4AF37",paddingHorizontal:20,paddingVertical:10}}>

          <Text style={{color:"white",fontFamily:"Poppins-Medium",}}>Go Back Home</Text>

        </TouchableOpacity> */}
        
      </View>

      ):
      <Text>
        hello
      </Text>
    }
      
    </View>
  );
};

export default MyTrips;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
  },
  logoandTitleWrapper: {
    flexDirection: "row",
    alignItems: "center",
    width: "82%",
  },
  NoTripSavedWrapper: {
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    height: "70%",
  },
});
