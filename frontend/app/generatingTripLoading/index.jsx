import { StyleSheet, Text, View, Alert } from 'react-native'
import { useEffect, useContext } from "react";
import LottieView from 'lottie-react-native';
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from '../../constants/themes'
import { useRouter } from 'expo-router';
import api from "../../src/services/api";
import Constants from 'expo-constants';
import { useItinerary } from "../contexts/itineraryContext";

const GeneratingTripLoader = () => {
  const { theme } = useContext(ThemeContext);
  const { itineraryItems, updateItineraryItem } = useItinerary();
  const router = useRouter();
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  // Fallback if extra is undefined (though it should be defined if configured correctly)
  const API_BASE_URL = Constants.expoConfig?.extra?.API_BASE_URL;
  console.log("DEBUG: Constants.expoConfig:", JSON.stringify(Constants.expoConfig, null, 2));
  console.log("DEBUG: Using API_BASE_URL:", API_BASE_URL);

  useEffect(() => {
    const generate = async () => {
      // 1. Get the last added itinerary item (which contains the preferences)
      if (itineraryItems.length === 0) {
        // Should not happen if flow is correct
        Alert.alert("Error", "No trip data found.");
        router.back();
        return;
      }

      const currentItem = itineraryItems[itineraryItems.length - 1];

      console.log("Generating itinerary for preferences:", currentItem.userPreferences);

      try {
        const response = await api.post(
          `${API_BASE_URL}/api/itinerary/generate/`,
          currentItem.userPreferences,
          { timeout: 6600000 }
        );

        if (response.status === 200) {
          console.log("Itinerary generated successfully");
          updateItineraryItem(currentItem.id, response.data);
          router.push("main/myTrips");
        }
      } catch (error) {
        console.error("Error generating itinerary:", error);
        // Alert.alert("Note", "Generation failed or timed out. Showing example itinerary instead.");
        // Proceed anyway so fallback data in ItineraryDetails takes over
        router.push("main/myTrips");
      }
    };

    generate();
  }, []);

  return (
    <View style={[styles.container, { backgroundColor: currentTheme.background }]}>
      <LottieView
        source={require('../../assets/images/trip.json')}
        autoPlay
        loop={true}
        speed={1.5}
        style={{ width: 300, height: 300 }}
      />
      <Text style={{ fontFamily: "Poppins-SemiBold", fontSize: 26, color: currentTheme.text }}>
        Generating Itinerary
      </Text>

      <Text style={{ fontFamily: "Poppins-Medium", fontSize: 15, color: currentTheme.description }}>
        Please Wait...
      </Text>
    </View>
  )
}

export default GeneratingTripLoader

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    flexDirection: 'column',
  }
})