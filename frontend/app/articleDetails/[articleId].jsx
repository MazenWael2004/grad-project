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
import api from "../../src/services/api";

import articles from "../../constants/articles";

const TripDetails = () => {
  const API_KEY = "ae7b6216e0c44cd6a3f163836252909";
  const [weather, setWeather] = useState(null);
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const { articleId } = useLocalSearchParams();
  const article = articles.find((item) => {
    return item.id === Number(articleId);
  });

  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 30 }}
      >
        <ImageBackground source={article.photo} style={styles.background}>
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
          </View>
        </ImageBackground>

        {article.content.map((item, index) => {
          return (
            <View key={index} style={styles.gettingToPlaceWrapper}>
              <Text
                style={{
                  fontFamily: "Poppins-ExtraBold",
                  fontSize: 18,
                  color: currentTheme.text,
                }}
              >
                {item.subheader}
              </Text>

             
{item.description.split('\n\n').map((paragraph, index) => (
  <Text
    key={index}
    style={{
      fontFamily: "Poppins-Medium",
      fontSize: 13,
      color: currentTheme.description,
      marginBottom: 10, // spacing between paragraphs
      lineHeight: 20,
    }}
  >
    {paragraph.trim()}
  </Text>
))}

            </View>
          );
        })}

        {/* <View style={styles.gettingToPlaceWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 18,
              color: currentTheme.text,
            }}
          >
            Published at 27 September 2025, Egypt Time Travel 
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
        </View> */}
      </ScrollView>
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
