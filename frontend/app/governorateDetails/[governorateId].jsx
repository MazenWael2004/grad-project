import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  ImageBackground,
  Image,
  TouchableOpacity,
} from "react-native";
import { router, useLocalSearchParams, useNavigation } from "expo-router";
import { useContext, useState, useEffect } from "react";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import governorates from "../../constants/governorates";
import axios from "axios";

const TripDetails = () => {
  const API_KEY = "ae7b6216e0c44cd6a3f163836252909";
  const [weather, setWeather] = useState(null);
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const { governorateId } = useLocalSearchParams();
  const governorate = governorates.find((item) => {
    return item.id === Number(governorateId);
  });

  const fetchWeather = async (city) => {
    try {
      const response = await axios.get(
        `http://api.weatherapi.com/v1/current.json`,
        {
          params: {
            key: API_KEY,
            q: city.toLowerCase(),
            aqi: "no",
          },
        }
      );
      setWeather(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    } finally {
      console.log("Weather fetch attempt finished.");
    }
  };

  useEffect(() => {
    fetchWeather(governorate.name);
  }, []);

  console.log(weather);

  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 30 }}
      >
        <ImageBackground source={governorate.image1} style={styles.background}>
          <View style={styles.backAndSaveButtonWrapper}>
            <TouchableOpacity
              style={[
                styles.button,
                { backgroundColor: currentTheme.searchBackground },
              ]}
              onPress={() => {
                router.back();
              }}
            >
              <Image
                source={require("../../assets/images/back.png")}
                style={{
                  width: 30,
                  height: 30,
                  tintColor: currentTheme.iconColor,
                }}
              />
            </TouchableOpacity>

            {/* <TouchableOpacity
              style={[styles.button,{backgroundColor:currentTheme.searchBackground}]}
              onPress={() => {
                console.log("Save Pressed!");
              }}
            >
              <Image
                source={require("../../assets/images/save.png")}
                style={{ width: 20, height: 20,tintColor:currentTheme.iconColor  }}
              />
            </TouchableOpacity> */}
          </View>
        </ImageBackground>

        

        <View style={styles.tripDescriptionWrapper}>
          <View style={styles.introductoryWrapper}>
            <Text style={[styles.tripNameStyle, { color: currentTheme.text }]}>
              {governorate.name}
            </Text>
              <View
          style={{
            height: 300,
            width: "100%",
            paddingHorizontal: 20,
            paddingTop: 20,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <View style={[styles.weatherContainer,{backgroundColor:weather?.current?.is_day?"#4FB4ED":"#185E89"}]}>
            <View
              style={{
                flexDirection: "row",
                justifyContent: "space-between",
                height: "auto",
              }}
            >
              <View style={{ flexDirection: "column", gap: 10 }}>
                <Text style={{ color: "white", fontFamily: "Poppins-Medium" }}>
                  Humidity: {weather?.current?.humidity}%
                </Text>

                <Text style={{ color: "white", fontFamily: "Poppins-Bold",fontSize:20 }}>
                  {weather?.current?.condition?.text}
                </Text>
              </View>
              <Image
                source={weather?.current?.is_day?require("../../assets/images/day.png"):require("../../assets/images/clear-night.png")}
                style={{ width: 70, height: 70,tintColor:"white" }}
              />
            </View>
            <View style={{flexDirection:"row",gap:10,marginTop:10,alignItems:"center",marginBottom:"auto",}}>
             <Image

             source={require("../../assets/images/location.png")}
             style={{width:30,height:30,tintColor:"white"}}
             />
             <Text style={{ color: "white", fontFamily: "Poppins-Regular",fontSize:14 }}>
           {weather?.location?.name}
             </Text>
            
            </View>
            <Text style={{color: "white", fontFamily: "Poppins-ExtraBold",fontSize:23}}>
              Temperature: {weather?.current?.temp_c}°C
            </Text>
          </View>
        </View>
            <View style={styles.locationRow}>
              <Image
                source={governorate.logo}
                style={{
                  width: 80,
                  height: 80,
                  borderRadius: 15,
                  marginBottom: 10,
                }}
              />
              {/* <Text style={[styles.locationText,{color:currentTheme.text}]}>Giza</Text> */}
            </View>
          </View>
          <Text
            style={[
              styles.tripDescriptionStyle,
              { color: currentTheme.description },
            ]}
          >
            {governorate.description}
          </Text>
        </View>

      

        <View style={styles.tripGalleryWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 18,
              color: currentTheme.text,
            }}
          >
            Gallery
          </Text>
          <View
            style={{
              flexDirection: "row",
              gap: 7,
              justifyContent: "space-between",
            }}
          >
            <Image
              style={{
                width: 110,
                height: 110,
                resizeMode: "cover",
                borderRadius: 15,
              }}
              source={governorate.image2}
            />
            <Image
              style={{
                width: 110,
                height: 110,
                resizeMode: "cover",
                borderRadius: 15,
              }}
              source={governorate.image3}
            />
            <Image
              style={{
                width: 110,
                height: 110,
                resizeMode: "cover",
                borderRadius: 15,
              }}
              source={governorate.image4}
            />
          </View>
        </View>

        {/* <View style={styles.gettingToPlaceWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 18,
              color: currentTheme.text,
            }}
          >
            Location:
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-Regular",
              fontSize: 13,
              color: currentTheme.description,
            }}
          >
            The Pyramids of Giza are situated in the Giza Governorate, to the west of the Egyptian capital of Cairo. They are located along Al-Haram Street in Giza.

          </Text>
        </View> */}

        <View style={styles.gettingToPlaceWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 18,
              color: currentTheme.text,
            }}
          >
            Best time to visit:
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-Regular",
              fontSize: 13,
              color: currentTheme.description,
            }}
          >
            {governorate.bestTimeToVisit}
          </Text>
        </View>

        <View style={styles.gettingToPlaceWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 18,
              color: currentTheme.text,
            }}
          >
            Activites and Experiences
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-Regular",
              fontSize: 13,
              color: currentTheme.description,
            }}
          >
            {governorate.experiences}
          </Text>
        </View>
      </ScrollView>
      <View
        style={{
          backgroundColor: currentTheme.background,
          padding: 20,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <TouchableOpacity
          style={{
            borderRadius: 30,
            backgroundColor: "#D4AF37",
            width: "100%",
            justifyContent: "center",
            alignItems: "center",
            padding: 12,
          }}
          onPress={() => {
            router.push(`/startTripQuestions/startTripQuestions`);
          }}
        >
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              color: "white",
              fontSize: 15,
            }}
          >
            Start a trip
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default TripDetails;

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  background: {
    width: "100%",
    height: 300,
    resizeMode: "cover",
  },
  backAndSaveButtonWrapper: {
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  button: {
    // backgroundColor: "#fff",
    borderRadius: 45,
    padding: 4,
    justifyContent: "center",
    alignItems: "center",
    width: "40",
    height: "40",
  },
  tripNameStyle: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 21,
    // color: "#333",
  },
  tripDescriptionWrapper: {
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  introductoryWrapper: {
    flexDirection: "column",
    gap: 5,
  },
  locationRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  locationText: {
    fontFamily: "Poppins-Regular",
    fontSize: 16,
    // color: "#666",
  },
  tripDescriptionStyle: {
    marginTop: 10,
    fontFamily: "Poppins-Regular",
    fontSize: 13,
    // color: "#666",
  },
  tripGalleryWrapper: {
    marginTop: 10,
    paddingHorizontal: 20,
    paddingTop: 20,
    flexDirection: "column",
    gap: 7,
  },
  gettingToPlaceWrapper: {
    paddingHorizontal: 20,
    paddingTop: 20,
    flexDirection: "column",
    gap: 10,
  },
  weatherContainer: {
    // backgroundColor: "#185E89", // Night Color
    borderRadius: 15,
    width: "100%",
    height: "85%",
    padding: 15,
  },
});
