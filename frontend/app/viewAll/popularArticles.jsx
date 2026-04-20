import { StyleSheet, Text, View,Image,TouchableOpacity,ScrollView} from 'react-native'
import {useContext} from 'react'
import { router } from "expo-router";
import PopularPlaceItem from '../../components/PopularItem';
import { ThemeContext } from "../../theme/ThemeContext";
import {LIGHT_THEME,DARK_THEME} from '../../constants/themes'
import articles from '../../constants/articles';
import PopularItem from '../../components/PopularItem';
import { useUserTravelPreferences } from "../contexts/userTravelPreferencesContext";

const PopularPlaces = () => {
  const {theme} = useContext(ThemeContext);
  const currentTheme = theme === "Light"?LIGHT_THEME:DARK_THEME;
  const {addGovernorateId} = useUserTravelPreferences();

  const handleArticlePress = (id)=>{
     addGovernorateId(id);
     router.push(`/articleDetails/${id}`);
   }
 
 

  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
  <View style={styles.logoandTitleWrapper}>
    <TouchableOpacity style={[styles.button,{backgroundColor:currentTheme.searchBackground}]} onPress={() => router.back()}>
      <Image
        source={require("../../assets/images/back.png")}
        style={{ width: 24, height: 24, resizeMode: "contain",tintColor:currentTheme.iconColor }}
      />
    </TouchableOpacity>
    <Text style={[styles.title,{color:currentTheme.text}]}>Popular Articles</Text>
  </View>
  <ScrollView
    showsVerticalScrollIndicator={false}
    contentContainerStyle={styles.scrollContent}
  >
    {/* ...your PopularPlaceItem components */}
    {articles.map((item,index)=>{
      return (
    <PopularItem
            key={index+1}
            image={item.photo}
            title={item.title}
            onPress={() => handleArticlePress(item.id)}
            imageWidth = {"100%"}
            imageHeight = {200}
          />
      )
    })}
    
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
  justifyContent: "center", // center contents
  position: "relative",
},

button: {
  position: "absolute", // fixes alignment issue
  left: 0,
  borderRadius: 20,
  padding: 8,
  elevation: 3,
  shadowColor: "#000",
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.08,
  shadowRadius: 4,
  width: 40,
  height: 40,
  justifyContent: "center",
  alignItems: "center",
},

title: {
  fontFamily: "Poppins-SemiBold",
  fontSize: 24,
  textAlign: "center",
  color: "#222", // fallback if theme text missing
},

  scrollContent: {
  paddingBottom: 30,
  flexDirection: "column",
  // remove alignItems: "center"
  // this lets items expand full width
},

});
