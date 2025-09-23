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
import { useContext } from "react";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";

const TripDetails = () => {
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const { tripId } = useLocalSearchParams();
  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{paddingBottom:30}}>
        <ImageBackground
          source={require("../../assets/images/giza.jpg")}
          style={styles.background}
        >
          <View style={styles.backAndSaveButtonWrapper}>
            <TouchableOpacity
              style={styles.button}
              onPress={() => {
                router.back();
              }}
            >
              <Image
                source={require("../../assets/images/back.png")}
                style={{ width: 30, height: 30 }}
              />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.button}
              onPress={() => {
                console.log("Save Pressed!");
              }}
            >
              <Image
                source={require("../../assets/images/save.png")}
                style={{ width: 20, height: 20 }}
              />
            </TouchableOpacity>
          </View>
        </ImageBackground>

        <View style={styles.tripDescriptionWrapper}>
          <View style={styles.introductoryWrapper}>
            <Text style={[styles.tripNameStyle,{color:currentTheme.text}]}>Pyramids of Giza</Text>
            <View style={styles.locationRow}>
              <Image
                source={require("../../assets/images/giza-governorate.png")}
                style={{ width: 40, height: 40 }}
              />
              <Text style={[styles.locationText,{color:currentTheme.text}]}>Giza</Text>
            </View>
          </View>
          <Text style={[styles.tripDescriptionStyle,{color:currentTheme.description}]}>
            Unveil the timeless wonder of the Pyramids of Giza, where ancient
            grandeur meets the endless desert horizon. Standing as eternal
            guardians of history, these colossal monuments whisper tales of
            pharaohs and forgotten dynasties. From the awe-inspiring Great
            Pyramid to the enigmatic Sphinx, Giza offers a journey through the
            cradle of civilization—an experience that bridges the past and the
            present in breathtaking harmony.
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
              gap: 10,
              justifyContent: "space-between",
            }}
          >
            <Image
              style={{
                width: 100,
                height: 100,
                resizeMode: "contain",
                borderRadius: 15,
              }}
              source={require("../../assets/images/sphinx.webp")}
            />
            <Image
              style={{
                width: 100,
                height: 100,
                resizeMode: "contain",
                borderRadius: 15,
              }}
              source={require("../../assets/images/pyramids4.jpg")}
            />
            <Image
              style={{
                width: 100,
                height: 100,
                resizeMode: "cover",
                borderRadius: 15,
              }}
              source={require("../../assets/images/pyramids5.jpg")}
            />
          </View>
        </View>

        <View style={styles.gettingToPlaceWrapper}>
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
        </View>

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
       The best time to visit Egypt pyramids would be from December to February if you want to enjoy cooler temperatures. If you want to avoid crowds, visit during the low season from May to September.
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
            Must-See Attractions:
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-Regular",
              fontSize: 13,
              color: currentTheme.description,
            }}
          >
         Explore the Great Pyramids of Giza, as well as the Great Sphinx and viewing the evening Sound and Light Show.
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
            Activities and Experiences: 
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-Regular",
              fontSize: 13,
              color: currentTheme.description,
            }}
          >
            The Great Pyramids of Giza offers a wide range of activites to do, from camel or horse riding,attending the Light and Sound Show,to taking phenomenal photos.
          </Text>
        </View>
      </ScrollView>
      <View style={{backgroundColor:currentTheme.background,padding:20,justifyContent:"center",alignItems:"center"}}>
      <TouchableOpacity style={{borderRadius:30,backgroundColor:"#D4AF37",width:"100%",justifyContent:"center",alignItems:"center",padding:12,}} onPress={()=>{router.push(`/startTripQuestions/startTripQuestions`)}}>
        <Text style={{fontFamily:"Poppins-Medium",color:"white",fontSize:15}}>
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
    backgroundColor: "#fff",
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
    marginTop: 10,
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
    gap: 10,
  },
  gettingToPlaceWrapper: {
    paddingHorizontal: 20,
    paddingTop: 20,
    flexDirection: "column",
    gap: 10,
  },
});
