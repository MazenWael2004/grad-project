import React, { useEffect, useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  BackHandler,
  Alert,
  SafeAreaView,
  Image,
  TextInput,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { SearchBar } from "react-native-screens";
import { CountryPicker } from "react-native-country-codes-picker";
import PopularPlaceItem from "../../components/PopularPlaceItem";

const Home = () => {
  useEffect(() => {
    const backAction = () => {
      // Exit the app directly
      BackHandler.exitApp();
      return true; // prevent default behavior
    };

    const backHandler = BackHandler.addEventListener(
      "hardwareBackPress",
      backAction
    );

    return () => backHandler.remove(); // cleanup
  }, []);

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
      <View style={styles.searchBarWrapper}>
        <TextInput
          style={styles.searchBar}
          placeholder="Search Governorates..."
          placeholderTextColor="#888"
          textAlignVertical="center"
        />

        <Image
          source={require("../../assets/images/magnifying-glass.png")}
          style={styles.searchIcon}
        />
      </View>
      <View style={styles.popularPlacesAndPopularArtclesWrapper}>
        <View style={styles.popularPlacesWrapper}>
          <View style={styles.popularPlacesTitleAndViewAllWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-SemiBold",
                fontSize: 20,
                color: "#333",
              }}
            >
              Popular Places
            </Text>
            <View
              style={{ flexDirection: "row", alignItems: "center", gap: 10 }}
            >
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 14,
                  color: "#D2691E",
                }}
              >
                View All
              </Text>
              <TouchableOpacity onPress={() => console.log("Image pressed!")}>
                <Image
                  source={require("../../assets/images/ancient.png")}
                  style={{ width: 35, height: 35, resizeMode: "contain" }}
                />
              </TouchableOpacity>
            </View>
          </View>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{paddingRight:30,fkexDirection:"row",alignItems:"center" }}> 
          {/* Popular Places Cards */}
          <PopularPlaceItem
            key={1}
            image={require("../../assets/images/giza.jpg")}
            title="Pyramids of Giza"
            governorateImage={require("../../assets/images/giza-governorate.png")}
            governorateName="Giza"
            onPress={() => console.log("Pyramids of Giza pressed!")}
            onSave={() => console.log("Saved Pyramids of Giza")}
          />
          
          <PopularPlaceItem
            key={2}
            image={require("../../assets/images/abu-simbel-temple.webp")}
            title="Abu Simbel Temples"
            governorateImage={require("../../assets/images/aswan-governorate.png")}
            governorateName="Aswan"
            onPress={() => console.log("Abu Simbel Temples pressed!")}
            onSave={() => console.log("Saved Abu Simbel Temples")}
          />

          <PopularPlaceItem
            key={3}
            image={require("../../assets/images/grand-egyptian-museum.jpg")}
            title="Grand Egyptian Museum"
            governorateImage={require("../../assets/images/giza-governorate.png")}
            governorateName="Giza"
            onPress={() => console.log("Grand Egyptian Museum pressed!")}
            onSave={() => console.log("Saved Grand Egyptian Museum")}
          />

          
          </ScrollView>
      </View>
    </View>
  );
};

export default Home;

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
  searchBarWrapper: {
    marginTop: 20,
    position: "relative",
    flexDirection: "row",
    alignItems: "center",
  },
  searchBar: {
    backgroundColor: "#e5e4e4ff",
    flex: 1,
    height: 65,
    borderRadius: 15,
    paddingLeft: 20,
    paddingRight: 50,
    fontFamily: "Poppins-Regular",
    fontSize: 14,
    color: "#333",
  },
  searchIcon: {
    position: "absolute",
    right: 20,
    width: 24,
    height: 24,
    tintColor: "#888",
  },

  popularPlacesAndPopularArtclesWrapper: {
    flexDirection: "column",
    marginTop: 30,
    gap: 20,
  },
  popularPlacesWrapper: {
    flexDirection: "column",
  },
  popularPlacesTitleAndViewAllWrapper: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
});
