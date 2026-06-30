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
import { useContext, useState } from "react";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import { AirbnbRating } from "react-native-ratings";
import MapView, { PROVIDER_GOOGLE, Marker } from "react-native-maps";
import { useItinerary } from "../contexts/itineraryContext";
import governorates from "../../constants/governorates";
import { landmarks } from '../../constants/landmarks';

const ItineraryDetails = () => {
  const { itineraryItems } = useItinerary();
  const { itineraryId } = useLocalSearchParams();
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);

  const itineraryItem = itineraryItems.find((item) => item.id === Number(itineraryId));

  // Handle case where governorateId might be in userPreferences (if API failed and we only have initial data)
  const govId = itineraryItem?.governorateId || itineraryItem?.userPreferences?.governorateId;
  const governorate = governorates.find((item) => item.id === govId);




  // Fallback data (Hardcoded values from previous version)
  const fallbackDetails = {
    trip_name: governorate?.name || "Trip Details",
    trip_dates: "Dec 12 - Dec 14, 2025",
    travelers_type: "Couple",
    luxury_level: "Luxury",
    landmarks: landmarks, // Imported from constants
    itinerary: [
      {
        day: "December 1",
        activities: [
          {
            title: "Pharaonic Village",
            description: "A living museum of Ancient Egyptian life.",
            rating: 4.0,
            reviews_count: 938,
            time: "08:00 AM - 3:00 PM",
            cost: "EGP 300",
            google_maps_url: "https://maps.google.com"
          }
        ]
      },
      { day: "December 2", activities: [] },
      { day: "December 3", activities: [] },
      { day: "December 4", activities: [] },
    ]
  };

  // Merge dynamic data with fallback, preferring dynamic if available
  const displayData = {
    trip_name: itineraryItem?.trip_name || fallbackDetails.trip_name,
    trip_dates: itineraryItem?.trip_dates || fallbackDetails.trip_dates,
    travelers_type: itineraryItem?.travelers_type || fallbackDetails.travelers_type,
    luxury_level: itineraryItem?.luxury_level || fallbackDetails.luxury_level,
    landmarks: (itineraryItem?.landmarks && itineraryItem.landmarks.length > 0) ? itineraryItem.landmarks : fallbackDetails.landmarks,
    itinerary: (itineraryItem?.itinerary && itineraryItem.itinerary.length > 0) ? itineraryItem.itinerary : fallbackDetails.itinerary
  };

  if (!itineraryItem) return <View><Text>Loading...</Text></View>;

  const currentDayPlan = displayData.itinerary[selectedDayIndex];

  const handleRegionChange = (region) => {
    // console.log(region);
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
          source={governorate?.image1 || require("../../assets/images/cairo4.jpg")} // Ensure you have a fallback if governorate is null
          style={styles.background}
        >
          <View style={styles.backAndSaveButtonWrapper}>
            <TouchableOpacity
              style={[styles.button, { backgroundColor: currentTheme.background }]}
              onPress={() => {
                router.back();
              }}
            >
              <Image
                source={require("../../assets/images/back.png")}
                style={{ width: 30, height: 30, tintColor: currentTheme.iconColor }}
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
              {displayData.trip_name}
            </Text>
            <View style={styles.locationRow}>
              <Text
                style={[
                  styles.locationText,
                  { color: currentTheme.description },
                ]}
              >
                {displayData.trip_dates} . {displayData.travelers_type} . {displayData.luxury_level}
              </Text>
            </View>
          </View>
          {/* All trips marked on Google Maps */}
          {/* MapView temporarily disabled
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
              latitude: displayData.landmarks?.[0]?.coordinate?.latitude || 30.0444,
              longitude: displayData.landmarks?.[0]?.coordinate?.longitude || 31.2357,
              latitudeDelta: 0.5,
              longitudeDelta: 0.5,
            }}
            showsUserLocation
            showsMyLocationButton
            provider={PROVIDER_GOOGLE}
            onRegionChange={handleRegionChange}
          >


            {(displayData.landmarks || []).map(({ id, title, description, coordinate, color }, index) => (
              <Marker
                key={id || index}
                identifier={id}
                coordinate={coordinate}
                title={title}
                description={description}
                pinColor={color}
              />
            ))}

          </MapView>
          */}
          <View style={{
              width: "100%",
              height: 250,
              backgroundColor: currentTheme.searchBackground,
              borderRadius: 15,
              justifyContent: "center",
              alignItems: "center",
              marginTop: 15,
              marginBottom: 15,
            }}>
            <Text style={{ color: currentTheme.description }}>Map temporarily disabled</Text>
          </View>
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
          {displayData.itinerary.map((dayPlan, index) => (
            <TouchableOpacity
              key={index}
              style={{
                borderRadius: 30,
                backgroundColor: selectedDayIndex === index ? "#D4AF37" : currentTheme.searchBackground,
                paddingHorizontal: 20,
                paddingVertical: 10,
              }}
              onPress={() => setSelectedDayIndex(index)}
            >
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 13,
                  color: selectedDayIndex === index ? "#FFF" : currentTheme.text,
                }}
              >
                {dayPlan.day.split(":")[0] || `Day ${index + 1}`}
              </Text>
            </TouchableOpacity>
          ))}
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
          {currentDayPlan ? (
            <>
              <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 18, color: currentTheme.text, marginBottom: 15 }}>
                {currentDayPlan.day}
              </Text>

              {currentDayPlan.activities.map((activity, index) => (
                <View key={index} style={[styles.placeItem, { backgroundColor: currentTheme.searchBackground, marginBottom: 20 }]}>
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
                      {activity.title}
                    </Text>

                    <Text style={{ fontFamily: "Poppins-Regular", fontSize: 13, color: currentTheme.description, marginBottom: 10 }}>
                      {activity.description}
                    </Text>

                    <View style={styles.infoRow}>
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
                        {activity.rating} ({activity.reviews_count} reviews)
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
                    <View style={styles.infoRow}>
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
                        {activity.time}
                      </Text>
                    </View>
                    <View style={styles.infoRow}>
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
                        {activity.cost}
                      </Text>
                    </View>

                    {activity.google_maps_url && (
                      <TouchableOpacity style={styles.infoRow}>
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
                    )}
                  </View>
                </View>
              ))}
            </>
          ) : (
            <Text style={{ color: currentTheme.description, textAlign: 'center', marginTop: 20 }}>
              No itinerary details available.
            </Text>
          )}
        </ScrollView>
      </ScrollView>
      {/* tour-guide */}

      <View
        style={{
          backgroundColor: currentTheme.background,
          padding: 20,
          paddingBottom: 35, 
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
            padding: 15,
            flexDirection: "row", 
            gap: 10,
          }}
          onPress={() => {
            router.push({ 
              pathname: "/tourGuide", 
              params: { itineraryId: itineraryId } 
            });
          }}
        >
          <Text style={{ fontSize: 18 }}>📸</Text>
          <Text
            style={{
              fontFamily: "Poppins-Medium",
              color: "white",
              fontSize: 16,
            }}
          >
            Open Tour Guide
          </Text>
        </TouchableOpacity>
      </View>
      {/* ------------------------------------- */}

    </View>
      /* <View
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
      </View> */
    // </View>
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
  infoRow: {
    flexDirection: "row",
    gap: 10,
    alignItems: "center",
    marginBottom: 10,
  },
  icon: {
    width: 25,
    height: 25,
  },
  infoText: {
    fontFamily: "Poppins-Medium",
    fontSize: 14,
    marginTop: 10,
  },
});
