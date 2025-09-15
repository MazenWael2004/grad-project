import { StyleSheet, Text, View,Image,TouchableOpacity,ScrollView} from 'react-native'
import React from 'react'
import { router } from "expo-router";
import PopularPlaceItem from '../../components/PopularPlaceItem';
const PopularPlaces = () => {
  return (
    <View style={styles.container}>
<View style={styles.logoandTitleWrapper}>
        <TouchableOpacity style={styles.button} onPress={()=>router.back()}>
         <Image
          source={require("../../assets/images/back.png")}
          style={{ width: 30, height:30, resizeMode: "contain" }}
        />
        </TouchableOpacity>
        
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 25,
            color: "#000000ff",
            margin: "auto",
          }}
        >
          Popular Places
        </Text>
      </View>
      <ScrollView
      showsVerticalScrollIndicator={false}
      contentContainerStyle={{
        paddingBottom:30,
        flexDirection:"column",
        alignItems:"center",
      }}
        >
            <PopularPlaceItem
            key={1}
            image={require("../../assets/images/giza.jpg")}
            title="Pyramids of Giza"
            governorateImage={require("../../assets/images/giza-governorate.png")}
            governorateName="Giza"
            onPress={() => router.push(`/tripDetails/1`)}
            onSave={() => console.log("Saved Pyramids of Giza")}
            imageWidth = {310}
            imageHeight = {290}
          />

        </ScrollView>
      
    </View>
  )
}

export default PopularPlaces

const styles = StyleSheet.create({
container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection:"column",
  },

   logoandTitleWrapper: {
    flexDirection: "row",
    justifyContent:"center",
    alignItems: "center",
    width: "95%",
    marginBottom:20,
  },

  button: {
    borderRadius: 45,
    padding: 4,
    justifyContent: "center",
    alignItems: "center",
    width: "40",
    height: "40",
  },

})