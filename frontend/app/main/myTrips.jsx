import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import React, { useState, useContext, useEffect } from "react";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import PopularItem from "../../components/PopularItem";
import { router } from "expo-router";
import { useItinerary } from "../contexts/itineraryContext";
import budgetOptions from "../../constants/budgetOptions";
import partyOptions from "../../constants/partyOptions";

const MyTrips = () => {
  const [isEmpty, setIsEmpty] = useState(false);
  const { theme } = useContext(ThemeContext);
  const [isActive, setIsActive] = useState(true);
  const [isPassed, setIsPassed] = useState(false);
  const { itineraryItems, addToItineraryList } = useItinerary();
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  
  useEffect(()=>{
    if(itineraryItems.length === 0) {
      setIsEmpty(true);
    }
  },[])
  console.log(itineraryItems);

  const toggleActiveButton = () => {
    setIsActive(true);
    setIsPassed(false);
  };

  const togglePassedButton = () => {
    setIsActive(false);
    setIsPassed(true);
  };

  const renderItineraryItems = () => {
  return itineraryItems.map((item) => {
    const userTravelPreferences = item["userPreferences"];

    const startDate = userTravelPreferences["startTripDate"];
    const endDate = userTravelPreferences["endTripDate"];
    const startTripDate = new Date(startDate);
    const endTripDate = new Date(endDate);

    const partyID = userTravelPreferences["partyId"];
    const partyOption = partyOptions.find((p) => p.id === partyID);

    const budgetID = userTravelPreferences["budgetId"];
    const budgetOption = budgetOptions.find((b) => b.id === budgetID);

    return (
      <PopularItem
        key={item.id}
        image={require("../../assets/images/giza.jpg")}
        title={"Giza Governorate"}
        smallDescription={`${startTripDate.toDateString()} - ${endTripDate.toDateString()} • ${
          partyOption.title
        } • ${budgetOption.title}`}
        onPress={() => router.push(`itineraryDetails/${item.id}`)}
        onSave={() => console.log(`Saved ${item.title}`)}
        imageWidth={"100%"}
        imageHeight={200}
        isArticle={true}
      />
    );
  });
};

  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <View style={styles.logoandTitleWrapper}>
        <Image
          source={require("../../assets/images/Pyramids.png")}
          style={{
            width: 55,
            height: 55,
            resizeMode: "contain",
            tintColor: currentTheme.appIconColor,
          }}
        />
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 22,
            color: currentTheme.text,
            margin: "auto",
          }}
        >
          My Trips
        </Text>
      </View>
      {isEmpty ? (
        <View style={styles.NoTripSavedWrapper}>
          <Image
            source={require("../../assets/images/gps.png")}
            style={{
              width: 100,
              height: 100,
              marginBottom: 50,
              tintColor: currentTheme.iconColor,
            }}
          />
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 29,
              color: currentTheme.text,
              marginBottom: 15,
            }}
          >
            Empty
          </Text>
          <Text
            style={{
              fontFamily: "Poppins-Regular",
              fontSize: 13,
              color: currentTheme.description,
              textAlign: "center",
              marginBottom: 10,
            }}
          >
            Let our AI create personalized trip plans just for you. Start
            planning now!
          </Text>
          {/* <TouchableOpacity style={{borderRadius:25,backgroundColor:"#D4AF37",paddingHorizontal:20,paddingVertical:10}}>

          <Text style={{color:"white",fontFamily:"Poppins-Medium",}}>Go Back Home</Text>

        </TouchableOpacity> */}
        </View>
      ) : (
        <>
          <View
            style={{
              width: "100%",
              height: 50,
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 20,
            }}
          >
            <TouchableOpacity
              style={[
                {
                  backgroundColor: currentTheme.searchBackground,
                  width: "50%",
                  height: "100%",
                  justifyContent: "center",
                  alignItems: "center",
                  borderRadius: 5,
                },
                isActive && { backgroundColor: "#D4AF37" },
              ]}
              onPress={toggleActiveButton}
            >
              <Text
                style={[
                  {
                    color: currentTheme.text,
                    fontFamily: "Poppins-SemiBold",
                  },
                  isActive && { color: "white" },
                ]}
              >
                Active
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                {
                  backgroundColor: currentTheme.searchBackground,
                  width: "50%",
                  height: "100%",
                  justifyContent: "center",
                  alignItems: "center",
                  borderRadius: 5,
                },
                isPassed && { backgroundColor: "#D4AF37" },
              ]}
              onPress={togglePassedButton}
            >
              <Text
                style={[
                  {
                    color: currentTheme.text,
                    fontFamily: "Poppins-SemiBold",
                  },
                  isPassed && { color: "white" },
                ]}
              >
                Passed
              </Text>
            </TouchableOpacity>
          </View>
          <ScrollView
            horizontal={false}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{
              paddingBottom: 120,
              flexDirection: "column",
              gap: 5,
            }}
          >
            {renderItineraryItems()}
            {/* <PopularItem
              key={1}
              image={require("../../assets/images/giza.jpg")}
              title="Giza Governorate"
              governorateImage={require("../../assets/images/aswan-governorate.png")}
              smallDescription="Dec 12 - Dec 14, 2025 . A Couple . Luxury "
              onPress={() => router.push(`itineraryDetails/${1}`)}
              onSave={() => console.log("Saved Abu Simbel Temples")}
              imageWidth={"100%"}
              imageHeight={200}
              isArticle={true}
            /> */}
          </ScrollView>
        </>
      )}
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
    marginBottom: 20,
  },
  NoTripSavedWrapper: {
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    height: "70%",
  },
});
