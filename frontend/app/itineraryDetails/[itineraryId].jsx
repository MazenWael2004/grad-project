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
import { AirbnbRating } from "react-native-ratings";
import MapView, { PROVIDER_GOOGLE,Marker } from "react-native-maps";
import { useItinerary } from "../contexts/itineraryContext";
import governorates from "../../constants/governorates";
import { landmarks } from '../../constants/landmarks';

const ItineraryDetails = () => {
  const {itineraryItems} = useItinerary();
  const { itineraryId } = useLocalSearchParams();
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const itineraryItem = itineraryItems.find((item)=>{
    return item.id === Number(itineraryId);
  })
  
  const governorate = governorates.find((item)=>{
    return item.id === itineraryItem.governorate_id;
  })
  console.log(itineraryItem);

  const handleRating = (rating) => {
    console.log("User rating:", rating);
  };

  const handleRegionChange = (region) =>{
    console.log(region);
  }

  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 30 }}
      >
        <ImageBackground
          source={governorate.image1}
          style={styles.background}
        >
          <View style={styles.backAndSaveButtonWrapper}>
            <TouchableOpacity
              style={[styles.button,{backgroundColor:currentTheme.background}]}
              onPress={() => {
                router.back();
              }}
            >
              <Image
                source={require("../../assets/images/back.png")}
                style={{ width: 30, height: 30,tintColor:currentTheme.iconColor }}
              />
            </TouchableOpacity>

            {/* <TouchableOpacity
              style={styles.button}
              onPress={() => {
                console.log("Save Pressed!");
              }}
            >
              <Image
                source={require("../../assets/images/save.png")}
                style={{ width: 20, height: 20 }}
              />
            </TouchableOpacity> */}
          </View>
        </ImageBackground>

        <View style={styles.tripDescriptionWrapper}>
          <View style={styles.introductoryWrapper}>
            <Text style={[styles.tripNameStyle, { color: currentTheme.text }]}>
              {governorate.name}
            </Text>
            <View style={styles.locationRow}>
              <Text
                style={[
                  styles.locationText,
                  { color: currentTheme.description },
                ]}
              >
                Dec 12 - Dec 14, 2025 . A Couple . Luxury
              </Text>
            </View>
          </View>
          {/* All trips marked on Google Maps */}
          <MapView
            style={{
              width: "100%",
              height: 250,
              backgroundColor: currentTheme.searchBackground,
              borderRadius: 15,
              justifyContent: "center",
              alignItems: "center",
              marginTop: 15,
              marginBottom: 15,
            }}
            initialRegion={{
              latitude: 30.06699114837697,
              longitude: 31.293998254151173,
              latitudeDelta: 0.1,
              longitudeDelta: 0.1,
              // 30.06699114837697, 31.293998254151173
            }}
            showsUserLocation
            showsMyLocationButton
            provider={PROVIDER_GOOGLE}
            onRegionChange={handleRegionChange}
          >

            
{landmarks.map(({ id, title, description, coordinate, color }) => (
          <Marker
            key={id}
            identifier={id}
            coordinate={coordinate}
            title={title}
            description={description}
            pinColor={color}
          />
        ))}

          </MapView>
        </View>

        <ScrollView
          horizontal={true}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{
            paddingHorizontal: 20,
            flexDirection: "row",
            gap: 10,
            marginTop: 20,
          }}
        >
          {/* Each day card */}
          <TouchableOpacity
            style={{
              borderRadius: 30,
              backgroundColor: currentTheme.searchBackground,
              paddingHorizontal: 20,
              paddingVertical: 10,
            }}
          >
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 13,
                color: currentTheme.text,
              }}
            >
              December 1
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={{
              borderRadius: 30,
              backgroundColor: currentTheme.searchBackground,
              paddingHorizontal: 20,
              paddingVertical: 10,
            }}
          >
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 13,
                color: currentTheme.text,
              }}
            >
              December 2
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={{
              borderRadius: 30,
              backgroundColor: currentTheme.searchBackground,
              paddingHorizontal: 20,
              paddingVertical: 10,
            }}
          >
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 13,
                color: currentTheme.text,
              }}
            >
              December 3
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={{
              borderRadius: 30,
              backgroundColor: currentTheme.searchBackground,
              paddingHorizontal: 20,
              paddingVertical: 10,
            }}
          >
            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 13,
                color: currentTheme.text,
              }}
            >
              December 4
            </Text>
          </TouchableOpacity>
        </ScrollView>
        {/* Recommended Places To Visit */}
        <ScrollView
          horizontal={false}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{
            paddingTop: 70,
            paddingHorizontal: 30,
            flexDirection: "column",
            gap: 30,
            paddingBottom: 100,
          }}
        >
          <View style={[styles.placeItem,{backgroundColor:currentTheme.searchBackground}]}>
            <Image
              source={require("../../assets/images/Pharaonic-Village.webp")}
              style={{
                width: "100%",
                height: 200,
                borderTopRightRadius: 10,
                borderTopLeftRadius: 10,
                resizeMode: "cover",
              }}
            />
            <View style={styles.placeDescription}>
              <Text style={[styles.placeTitle, { color: currentTheme.text }]}>
                Pharaonic Vilage
              </Text>
              <View
                style={{
                  flexDirection: "row",
                  gap: 10,
                  alignItems: "center",
                  marginBottom: 10,
                }}
              >
                <Image
                  source={require("../../assets/images/review.png")}
                  style={{
                    width: 30,
                    height: 30,
                    tintColor: currentTheme.iconColor,
                  }}
                />
                <Text
                  style={{
                    fontFamily: "Poppins-Regular",
                    color: currentTheme.description,
                    marginTop: 10,
                  }}
                >
                  (4.0) 938 reviews
                </Text>
              </View>
              <View
                style={{
                  borderWidth: 0.2,
                  borderColor: currentTheme.description,
                  width: "100%",
                  marginBottom: 10,
                }}
              ></View>
              <View
                style={{
                  flexDirection: "row",
                  gap: 10,
                  alignItems: "center",
                  marginBottom: 10,
                }}
              >
                <Image
                  source={require("../../assets/images/clock.png")}
                  style={{
                    width: 25,
                    height: 25,
                    tintColor: currentTheme.iconColor,
                  }}
                />
                <Text
                  style={{
                    fontFamily: "Poppins-Medium",
                    fontSize: 14,
                    color: currentTheme.text,
                    marginTop: 10,
                  }}
                >
                  08:00 AM - 3:00 PM
                </Text>
              </View>
              <View
                style={{
                  flexDirection: "row",
                  gap: 10,
                  alignItems: "center",
                  marginBottom: 10,
                }}
              >
                <Image
                  source={require("../../assets/images/pound.png")}
                  style={{
                    width: 25,
                    height: 25,
                    tintColor: currentTheme.iconColor,
                  }}
                />
                <Text
                  style={{
                    fontFamily: "Poppins-Medium",
                    fontSize: 14,
                    color: currentTheme.text,
                    marginTop: 10,
                  }}
                >
                  EGP 300
                </Text>
              </View>

              <TouchableOpacity
                style={{
                  flexDirection: "row",
                  gap: 10,
                  alignItems: "center",
                  marginBottom: 10,
                }}
              >
                <Image
                  source={require("../../assets/images/location.png")}
                  style={{ width: 20, height: 20, tintColor: "#D4AF37" }}
                />
                <Text
                  style={{
                    fontFamily: "Poppins-Medium",
                    fontSize: 14,
                    color: "#D4AF37",
                    marginTop: 10,
                  }}
                >
                  View on Google Maps
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </ScrollView>
      {/* <View
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
      </View> */}
    </View>
  );
};

export default ItineraryDetails;

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
  },
  locationText: {
    fontFamily: "Poppins-Regular",
    fontSize: 13,
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
  placeItem: {
    flexDirection: "column",
    height: "auto",
    borderWidth: 0.15,
    borderRadius: 15,
    borderColor: "#333",
  },
  placeDescription: {
    padding: 15,
    flexDirection: "column",
    gap: 5,
  },
  placeTitle: {
    fontFamily: "Poppins-Bold",
    fontSize: 16,
  },
});
