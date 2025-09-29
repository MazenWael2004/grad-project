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
import governorates from "../../constants/governorates";
import { useSavedList } from "../contexts/savedListContext";
import { Provider as PaperProvider, Snackbar } from 'react-native-paper';

const MyTrips = () => {
  const {savedList} = useSavedList();
  const [isEmpty, setIsEmpty] = useState(false);
  const { theme } = useContext(ThemeContext);
  const [isActive, setIsActive] = useState(true);
  const [isPassed, setIsPassed] = useState(false);

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  

  useEffect(()=>{
   if(savedList.length === 0){
    setIsEmpty(true);
   } 
   else{
    setIsEmpty(false);
   }
  },[savedList]);
  

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
            marginLeft: "auto",
          }}
        >
          Saved 
        </Text>
      </View>
      {isEmpty ? (
        <View style={styles.NoTripSavedWrapper}>
          <Image
            source={require("../../assets/images/save-instagram.png")}
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
           Start building your travel wishlist by saving governorates.
          </Text>
          {/* <TouchableOpacity style={{borderRadius:25,backgroundColor:"#D4AF37",paddingHorizontal:20,paddingVertical:10}}>

          <Text style={{color:"white",fontFamily:"Poppins-Medium",}}>Go Back Home</Text>

        </TouchableOpacity> */}
        </View>
      ) : (
        <>
         <ScrollView showsVerticalScrollIndicator={false}>
          {savedList.map((item,index)=>{
            return(
              <PopularItem
              key = {index+1}
              image = {item.image1}
              title = {item.name}
              onPress = {()=> router.push(`/governorateDetails/${item.id}`)}
              imageWidth={"100%"}
              imageHeight={200}
              isArticle = {true}
              />
            )
          })}
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
    position:"relative",
  },
  logoandTitleWrapper: {
    flexDirection: "row",
    alignItems: "center",
   width:'60%',
    marginBottom: 20,
  },
  NoTripSavedWrapper: {
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    height: "70%",
  },
});
