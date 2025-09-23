import { StyleSheet, Text, View,Image,TouchableOpacity,ScrollView} from 'react-native'
import {useContext} from 'react'
import { router } from "expo-router";
import PopularPlaceItem from '../../components/PopularItem';
import { ThemeContext } from "../../theme/ThemeContext";
import {LIGHT_THEME,DARK_THEME} from '../../constants/themes'

const PopularPlaces = () => {
  const {theme} = useContext(ThemeContext);
  const currentTheme = theme === "light"?LIGHT_THEME:DARK_THEME;
  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
  <View style={styles.logoandTitleWrapper}>
    <TouchableOpacity style={[styles.button,{backgroundColor:currentTheme.backBackground}]} onPress={() => router.back()}>
      <Image
        source={require("../../assets/images/back.png")}
        style={{ width: 24, height: 24, resizeMode: "contain" }}
      />
    </TouchableOpacity>
    <Text style={[styles.title,{color:currentTheme.text}]}>Popular Places</Text>
  </View>
  <ScrollView
    showsVerticalScrollIndicator={false}
    contentContainerStyle={styles.scrollContent}
  >
    {/* ...your PopularPlaceItem components */}
    <PopularPlaceItem
            key={1}
            image={require("../../assets/images/giza.jpg")}
            title="Pyramids of Giza"
            governorateImage={require("../../assets/images/giza-governorate.png")}
            governorateName="Giza"
            onPress={() => router.push(`/tripDetails/1`)}
            onSave={() => console.log("Saved Pyramids of Giza")}
            imageWidth = {350}
            imageHeight = {200}
          />
  </ScrollView>
</View>

  )
}

export default PopularPlaces

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 60,
    paddingHorizontal: 20,
    // backgroundColor: "#F8F9FB", // Soft background
  },

  logoandTitleWrapper: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 25,
    width: "100%",
    justifyContent: "flex-start",
    position: "relative",
  },

  button: {
    borderRadius: 20,
    padding: 8,
    // backgroundColor: "#fff",
    elevation: 3, // Android shadow
    shadowColor: "#000", // iOS shadow
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    marginRight: 10,
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
  },

  title: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 24,
    // color: "#22223B",
    flex: 1,
    textAlign: "center",
    marginRight: 40, // To offset the back button
  },

  scrollContent: {
    paddingBottom: 30,
    flexDirection: "column",
    alignItems: "center",
  },
});
