import { StyleSheet, Text, View, TouchableOpacity, Image, ImageBackground } from "react-native";
import {useContext} from "react";
import { ThemeContext } from "../theme/ThemeContext";
import { LIGHT_THEME,DARK_THEME } from "../constants/themes";

const PopularItem = (props) => {
  const {theme,toggleTheme,setTheme} = useContext(ThemeContext);
  const currentTheme = theme === "Light"? LIGHT_THEME: DARK_THEME;
  return (
    <TouchableOpacity onPress={props.onPress} style={{ marginBottom: 20 }}>
      <ImageBackground

        source={props.image}
        style={[styles.image,{height:props.imageHeight,width:props.imageWidth}]}
        imageStyle={{ borderRadius: 15 }}
      >
        {
          !props.isArticle && (
        <TouchableOpacity
          style={styles.saveButton}
          onPress={props.onSave}
        >
         
          <Image
            source={require("../assets/images/save.png")}
            style={{ width: 20, height: 20, resizeMode: "contain",tintColor:"#c84c1fff" }}
          />
        </TouchableOpacity>)
        }
        
      </ImageBackground>

      {/* Title */}
      <Text style={[styles.title,{color:currentTheme.text}]}>{props.title}</Text>

      {/* Governorate Info */}
      <View style={styles.locationRow}>
         {
            !props.isArticle && (
               <Image
          source={props.governorateImage}
          style={{ width: 40, height: 40 }}
        />
            )
          }
       
        <Text style={[styles.locationText,{color:currentTheme.description}]}>{props.smallDescription}</Text>
      </View>
  
    </TouchableOpacity>
  );
};

export default PopularItem;

const styles = StyleSheet.create({
  image: {
    // width: 280,
    // height: 180,
    marginRight: 15,
    resizeMode: "cover",
    justifyContent: "flex-start",
  },
  saveButton: {
    position: "absolute",
    top: 10,
    right: 10,
    backgroundColor: "#fff",
    padding: 5,
    borderRadius: 50,
  },
  title: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 16,
    // color: "#333",
    marginTop: 15.5,
    width:"100%",
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
});
