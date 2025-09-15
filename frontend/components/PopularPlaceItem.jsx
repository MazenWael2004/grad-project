import { StyleSheet, Text, View, TouchableOpacity, Image, ImageBackground } from "react-native";
import React from "react";

const PopularPlaceItem = (props) => {
  return (
    <TouchableOpacity onPress={props.onPress} style={{ marginBottom: 20 }}>
      <ImageBackground

        source={props.image}
        style={[styles.image,{height:props.imageHeight,width:props.imageWidth}]}
        imageStyle={{ borderRadius: 15 }}
      >
        {/* Floating Save Button */}
        <TouchableOpacity
          style={styles.saveButton}
          onPress={props.onSave}
        >
          <Image
            source={require("../assets/images/save.png")}
            style={{ width: 20, height: 20, resizeMode: "contain",tintColor:"#c84c1fff" }}
          />
        </TouchableOpacity>
      </ImageBackground>

      {/* Title */}
      <Text style={styles.title}>{props.title}</Text>

      {/* Governorate Info */}
      <View style={styles.locationRow}>
        <Image
          source={props.governorateImage}
          style={{ width: 40, height: 40 }}
        />
        <Text style={styles.locationText}>{props.governorateName}</Text>
      </View>
  
    </TouchableOpacity>
  );
};

export default PopularPlaceItem;

const styles = StyleSheet.create({
  image: {
    // width: 280,
    // height: 180,
    marginRight: 15,
    resizeMode: "cover",
    justifyContent: "flex-start",
  },
  saveButton: {
    position: "absolute",
    top: 10,
    right: 10,
    backgroundColor: "#fff",
    padding: 5,
    borderRadius: 50,
  },
  title: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 18,
    color: "#333",
    marginTop: 15,
  },
  locationRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginTop: 10,
  },
  locationText: {
    fontFamily: "Poppins-Regular",
    fontSize: 16,
    color: "#666",
  },
});
