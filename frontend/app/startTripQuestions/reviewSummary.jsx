import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  ScrollView,
} from "react-native";
import { useContext,useEffect } from "react";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import PreferenceItem from "../../components/PreferenceItem";
import partyOptions from "../../constants/partyOptions";
import budgetOptions from "../../constants/budgetOptions";
import { useUserTravelPreferences } from "../contexts/userTravelPreferencesContext";
import preferences from "../../constants/preferences";

const ReviewSummary = () => {
  const { theme } = useContext(ThemeContext);
  const {userTravelPreferences} = useUserTravelPreferences();
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const startDate = userTravelPreferences['startTripDate'];
  const endDate = userTravelPreferences['endTripDate'];
  const startTripDate = new Date(startDate);
  const endTripDate = new Date(endDate);
  const interests = userTravelPreferences['interests']; // [3,5,6]
  const userInterests = preferences.filter(pref => interests.includes(pref.id-1));
  
  
const getMonthAndDay = (date) => {
  const options = { month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
};



// console.log("Start Trip:", getMonthAndDay(startTripDate)); // September 26
// console.log("End Trip:", getMonthAndDay(endTripDate));     // September 30

  const partyID = userTravelPreferences['partyId'];
  const partyOption = partyOptions.find((item)=>{
    return item.id === partyID;
  })

  const budgetID = userTravelPreferences['budgetId'];
  const budgetOption = budgetOptions.find((item)=>{
    return item.id === budgetID;
  });


  
  console.log(partyOption);
  useEffect(()=>{
    console.log(userTravelPreferences);
  },[]);

  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <View style={styles.backAndPersonalInfoTitle}>
        <TouchableOpacity onPress={() => router.back()}>
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

      <View style={styles.sectionWrapper}>
        <View style={styles.sectionItem}>
          <Image
            source={require("../../assets/images/location.png")}
            style={{ width: 25, height: 25, tintColor: currentTheme.iconColor }}
          />
          <View style={styles.sectionDescriptionWrapper}>
            <Text
              style={{
                fontSize: 16,
                fontFamily: "Poppins-SemiBold",
                color: currentTheme.text,
              }}
            >
              Destination
            </Text>
            <View style={{ flexDirection: "row", gap: 20 }}>
              <View
                style={{
                  width: 130,
                  height: 100,
                  borderRadius: 15,
                  overflow: "hidden",
                }}
              >
                <Image
                  source={require("../../assets/images/giza.jpg")}
                  style={{ width: "100%", height: "100%", resizeMode: "cover" }}
                />
              </View>
              <View style={{ flexDirection: "column", gap: 10 }}>
                <Text
                  style={{
                    fontFamily: "Poppins-SemiBold",
                    fontSize: 14,
                    color: currentTheme.text,
                  }}
                >
                  Giza Governorate
                </Text>

                <Image
                  source={require("../../assets/images/giza-governorate.png")}
                  style={{ width: 40, height: 40 }}
                />
              </View>
            </View>
          </View>
        </View>

        <View
          style={{
            borderWidth: 0.4,
            borderColor: currentTheme.description,
            marginTop: 4,
          }}
        ></View>

        <View style={styles.sectionItem}>
          <Image
            source={require("../../assets/images/group.png")}
            style={{ width: 25, height: 25, tintColor: currentTheme.iconColor }}
          />
          <View style={styles.sectionDescriptionWrapper}>
            <Text
              style={{
                fontSize: 16,
                fontFamily: "Poppins-SemiBold",
                color: currentTheme.text,
              }}
            >
              Party
            </Text>

            <Text
              style={{
                fontFamily: "Poppins-Regular",
                fontSize: 16,
                color: currentTheme.text,
              }}
            >
              {partyOption['title']}
            </Text>
          </View>
        </View>

        <View
          style={{
            borderWidth: 0.4,
            borderColor: currentTheme.description,
            marginTop: 4,
            marginBottom: 4,
          }}
        ></View>

        <View style={styles.sectionItem}>
          <Image
            source={require("../../assets/images/calendar.png")}
            style={{ width: 25, height: 25, tintColor: currentTheme.iconColor }}
          />
          <View style={styles.sectionDescriptionWrapper}>
            <Text
              style={{
                fontSize: 16,
                fontFamily: "Poppins-SemiBold",
                color: currentTheme.text,
              }}
            >
              Trip Dates
            </Text>

            <Text
              style={{
                fontFamily: "Poppins-Regular",
                fontSize: 16,
                color: currentTheme.text,
              }}
            >
              {getMonthAndDay(startTripDate)} to {getMonthAndDay(endTripDate)}, 2025
            </Text>
          </View>
        </View>

        <View
          style={{
            borderWidth: 0.4,
            borderColor: currentTheme.description,
            marginTop: 4,
            marginBottom: 4,
          }}
        ></View>

        <View style={styles.sectionItem}>
          <Image
            source={require("../../assets/images/star.png")}
            style={{ width: 25, height: 25, tintColor: currentTheme.iconColor }}
          />
          <View style={styles.sectionDescriptionWrapper}>
            <Text
              style={{
                fontSize: 16,
                fontFamily: "Poppins-SemiBold",
                color: currentTheme.text,
              }}
            >
              Interests
            </Text>

            <View style={styles.preferencesContainer}>
             {userInterests.map((item,index)=>{
              return(
                <PreferenceItem key = {index} title={item.title} />
              )
             })}
            </View>
          </View>
        </View>

        <View
          style={{
            borderWidth: 0.4,
            borderColor: currentTheme.description,
            marginTop: 4,
            marginBottom: 4,
          }}
        ></View>

        <View style={styles.sectionItem}>
          <Image
            source={require("../../assets/images/budgeting.png")}
            style={{ width: 25, height: 25, tintColor: currentTheme.iconColor }}
          />
          <View style={styles.sectionDescriptionWrapper}>
            <Text
              style={{
                fontSize: 16,
                fontFamily: "Poppins-SemiBold",
                color: currentTheme.text,
              }}
            >
              Budget
            </Text>

            <Text
              style={{
                fontFamily: "Poppins-Regular",
                fontSize: 16,
                color: currentTheme.text,
              }}
            >
              {budgetOption['title']}
            </Text>
          </View>
        </View>

        <View
          style={{
            borderWidth: 0.4,
            borderColor: currentTheme.description,
            marginTop: 4,
            marginBottom: 4,
          }}
        ></View>
      </View>
      <TouchableOpacity
        style={{
          borderRadius: 20,
          backgroundColor: "#D4AF37",
          justifyContent: "center",
          alignItems: "center",
          padding: 14,
          width:'100%',
          marginTop:20,
        }}

        onPress={()=>router.push("/generatingTripLoading")}
      >
        <Text
          style={{ fontFamily: "Poppins-Medium", color: "white", fontSize: 17 }}
        >
          Build My Itinerary
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
    marginBottom: 45,
  },
  sectionWrapper: {
    flexDirection: "column",
    gap: 10,
  },
  sectionItem: {
    flexDirection: "row",
    gap: 15,
  },
  sectionDescriptionWrapper: {
    width: "90%",
    flexDirection: "column",
    gap: 10,
  },
  preferencesContainer: {
    flexDirection: "row",
    gap: 14,
    marginTop: 10,
    height: "auto",
    flexWrap: "wrap",
  },
});
