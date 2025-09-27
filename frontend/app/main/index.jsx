import React, { useCallback,useContext, useEffect, useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  BackHandler,
  Image,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Platform,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native"; // 👈 add this
import PopularItem from "../../components/PopularItem";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME,DARK_THEME } from "../../constants/themes";
import governorates from "../../constants/governorates";

const Home = () => {
  const {theme} = useContext(ThemeContext);
  const [input,setInput] = useState("");
  const [isInputEmpty,setIsInputEmpty] = useState(false);
  const [filteredGovernorates,setFilteredGovernorates] = useState([]);
  


  const handleGovernorateInput = (text)=>{
    setInput(text);
    console.log(text);
  }
  // useEffect(()=>{
  //   toggleTheme();
  // },[])

  useEffect(()=>{
    if(input === ''){
      setIsInputEmpty(true);
    }
    else{
      setIsInputEmpty(false);
      setFilteredGovernorates(governorates.filter((item) =>
      item.name.toLowerCase().includes(input.toLowerCase()))
     
);

    }
  },[input])


  const currentTheme = theme === "Light"? LIGHT_THEME: DARK_THEME;
  console.log(currentTheme);
  const width = 200;
  const height = 140;
  useFocusEffect(
    useCallback(() => {
      if (Platform.OS !== "android") return; // only matters on Android

      const onBackPress = () => {
        // Exit the app directly (only for this screen)
        BackHandler.exitApp();
        return true; // prevent default behavior
      };

      const sub = BackHandler.addEventListener(
        "hardwareBackPress",
        onBackPress
      );
      return () => sub.remove();
    }, [])
  );

  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
      <View style={styles.logoandTitleWrapper}>
        <Image
          source={require("../../assets/images/Pyramids.png")}
          style={{ width: 55, height: 55, resizeMode: "contain",tintColor:currentTheme.appIconColor }}
        />
        <Text
          style={{
            fontFamily: "Poppins-ExtraBold",
            fontSize: 30,
            color: "#D2691E",
            margin: "auto",
          }}
        >
          Historai
        </Text>
        <TouchableOpacity style={{backgroundColor:currentTheme.searchBackground,padding:6,borderRadius:30,justifyContent:"center",alignItems:"center"}} onPress={()=>router.push('/chatbot')}>
          <Image
          source={require("../../assets/images/robot.png")}
          style={{width:45,height:45}}
          />
        </TouchableOpacity>
      </View>

      <View style={styles.searchBarWrapper}>
        <TextInput
          style={[styles.searchBar,{backgroundColor:currentTheme.searchBackground,color:currentTheme.text}]}
          placeholder="Search Governorates..."
          placeholderTextColor="#888"
          textAlignVertical="center"
          onChangeText={handleGovernorateInput}
        />
        <Image
          source={require("../../assets/images/magnifying-glass.png")}
          style={styles.searchIcon}
        />
      </View>
      {
        isInputEmpty?(
                <ScrollView contentContainerStyle={{ paddingBottom: 100 }} showsVerticalScrollIndicator={false}>
      <View style={styles.popularPlacesAndPopularArtclesWrapper}>
        <View style={styles.popularPlacesWrapper}>
          <View style={styles.popularPlacesTitleAndViewAllWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-SemiBold",
                fontSize: 20,
                color: currentTheme.text,
              }}
            >
              Popular Places
            </Text>
            <View
              style={{ flexDirection: "row", alignItems: "center", gap: 10 }}
            >
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 14,
                  color: "#D2691E",
                }}
              >
                View All
              </Text>
              <TouchableOpacity
                onPress={() => router.push("viewAll/popularPlaces")}
              >
                <Image
                  source={require("../../assets/images/ancient.png")}
                  style={{ width: 35, height: 35, resizeMode: "contain" }}
                />
              </TouchableOpacity>
            </View>
          </View>
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{
            paddingRight: 30,
            flexDirection: "row", // 👈 fixed typo: fkexDirection -> flexDirection
            alignItems: "center",
            marginTop:1,
            gap:15,
          }}
        >
          {/* Popular Places Cards */}
          {governorates.map((item,index)=>{
            return(
              <PopularItem
              key = {index+1}
              image = {item.image1}
              title = {item.name}
              onPress = {()=> router.push(`/governorateDetails/${item.id}`)}
              onSave = {()=>console.log("Saved!")}
              imageWidth={width}
              imageHeight={height}
              isArticle = {false}
              />
            )
          })}
          {/* <PopularItem
            key={1}
            image={require("../../assets/images/giza.jpg")}
            title="Giza Governorate"
            onPress={() => router.push(`/governorateDetails/1`)}
            onSave={() => console.log("Saved Pyramids of Giza")}
            imageWidth={width}
            imageHeight={height}
            isArticle={false}
          /> */}

          {/* <PopularItem
            key={2}
            image={require("../../assets/images/cairo1.webp")}
            title="Cairo Governorate"
            onPress={() => console.log("Abu Simbel Temples pressed!")}
            onSave={() => console.log("Saved Abu Simbel Temples")}
            imageWidth={width}
            imageHeight={height}
            isArticle={false}
          />

          <PopularItem
            key={3}
            image={require("../../assets/images/grand-egyptian-museum.jpg")}
            title="Grand Egyptian Museum"
            governorateImage={require("../../assets/images/giza-governorate.png")}
            smallDescription="Giza"
            onPress={() => console.log("Grand Egyptian Museum pressed!")}
            onSave={() => console.log("Saved Grand Egyptian Museum")}
            imageWidth={width}
            imageHeight={height}
            isArticle={false}
          /> */}
        </ScrollView>
        
        <View style={styles.popularArticlesContainer}>
          <View style={styles.popularPlacesTitleAndViewAllWrapper}>
            <Text
              style={{
                fontFamily: "Poppins-SemiBold",
                fontSize: 20,
                color: currentTheme.text,
              }}
            >
              Popular Articles
            </Text>
            <View
              style={{ flexDirection: "row", alignItems: "center", gap: 10 }}
            >
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 14,
                  color: "#D2691E",
                }}
              >
                View All
              </Text>
              <TouchableOpacity
                onPress={() => router.push("viewAll/popularArticles")}
              >
                <Image
                  source={require("../../assets/images/ancient.png")}
                  style={{ width: 35, height: 35, resizeMode: "contain" }}
                />
              </TouchableOpacity>
            </View>
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{
              paddingRight: 30,
              flexDirection: "row", // 👈 fixed typo: fkexDirection -> flexDirection
              alignItems: "center",
            }}
          >
            <PopularItem
              key={1}
              image={require("../../assets/images/tourism1.jpg")}
              title="Egypt Among the World's Best."
              isArticle={true}
              smallDescription="09 Jul 2025"
              onPress={() => router.push(`/tripDetails/1`)}
              onSave={() => console.log("Saved Pyramids of Giza")}
              imageWidth={width}
              imageHeight={height}
            />
          </ScrollView>
        </View>
      </View>
      </ScrollView>
        ):(
          <>
          <Text style={{fontFamily:"Poppins-SemiBold",marginTop:20,color:currentTheme.text,fontSize:19,marginBottom:20}}>
            Search Results: {filteredGovernorates.length}
          </Text>

          <ScrollView horizontal={false} showsVerticalScrollIndicator={false} contentContainerStyle={{paddingBottom:45,flexDirection:"column"}}>
            {filteredGovernorates.map((item,index)=>{
            return(
              <PopularItem
              key = {index+1}
              image = {item.image1}
              title = {item.name}
              onPress = {()=> router.push(`/governorateDetails/${item.id}`)}
              onSave = {()=>console.log("Saved!")}
              imageWidth={"100%"}
              imageHeight={250}
              isArticle = {false}
              />
            )
          })}

          </ScrollView>
          </>
        )
      }

    </View>
  );
};

export default Home;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    
  },
  logoandTitleWrapper: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent:"space-between",
    width: "100%",
  },
  searchBarWrapper: {
    marginTop: 20,
    position: "relative",
    flexDirection: "row",
    alignItems: "center",
  },
  searchBar: {
    // backgroundColor: "#e5e4e4ff",
    flex: 1,
    height: 65,
    borderRadius: 15,
    paddingLeft: 20,
    paddingRight: 50,
    fontFamily: "Poppins-Regular",
    fontSize: 14,
    color: "#333",
  },
  searchIcon: {
    position: "absolute",
    right: 20,
    width: 24,
    height: 24,
    tintColor: "#888",
  },

  popularPlacesAndPopularArtclesWrapper: {
    flexDirection: "column",
    marginTop: 30,
    
  },
  popularPlacesWrapper: {
    flexDirection: "column",
  },
  popularPlacesTitleAndViewAllWrapper: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  popularArticlesContainer: {
  marginTop: -30, // controls spacing between Governorates & Articles
}

});
