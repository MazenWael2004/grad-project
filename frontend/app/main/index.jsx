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
import {useSavedList} from "../contexts/savedListContext"
import { useUserTravelPreferences } from "../contexts/userTravelPreferencesContext";
import articles from "../../constants/articles";
import { useUser } from "../contexts/userContext";


const Home = () => {
  const { user, setUser } = useUser();
  const {theme} = useContext(ThemeContext);
  const {addGovernorateId} = useUserTravelPreferences();
  const [input,setInput] = useState("");
  const [isInputEmpty,setIsInputEmpty] = useState(false);
  const [filteredGovernorates,setFilteredGovernorates] = useState([]);
  const {savedList,addToSavedList,removeFromSavedList} = useSavedList();
  console.log("User Data",user);

  

  const handleGovernoratePress = (id)=>{
    addGovernorateId(id);
    router.push(`/governorateDetails/${id}`);
  }


  const handleGovernorateInput = (text)=>{
    setInput(text);
    console.log(text);
  }
  useEffect(()=>{
      console.log("Saved List",savedList)
  },[savedList])

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

  const toggleSaveButton = (item)=>{
    if(item.isSaved){
      removeFromSavedList(item.id)
      item.isSaved = false;
    }
    else{
    addToSavedList(item);
    item.isSaved = true;
    }
  };

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
              onPress = {()=> handleGovernoratePress(item.id)}
              onSave = {()=>{toggleSaveButton(item)}}
              imageWidth={width}
              imageHeight={height}
              isArticle = {false}
              isSaved = {item.isSaved}
              />
            )
          })}
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
            horizontal={false}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{
              // paddingRight: 30,
              flexDirection: "column", // 👈 fixed typo: fkexDirection -> flexDirection
  
            }}
          >
            {articles.map((item,indx)=>{
              return (
              <PopularItem
              key={indx}
              image={item.photo}
              title={item.title}
              isArticle={true}
              smallDescription={`${item.publisher}, ${item.published_date}`}
              onPress={() => router.push(`/articleDetails/${item.id}`)}
              imageWidth={"100%"}
              imageHeight={160}
            />
              )
            })}
           
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
