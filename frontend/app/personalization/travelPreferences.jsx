import { StyleSheet, Text, View, TouchableOpacity, Image } from "react-native";
import React,{useState} from "react";
import * as Progress from "react-native-progress";
import { useRouter } from "expo-router"; 
import PreferenceItem from "../../components/PreferenceItem";

const TravelPreferences = () => {
  const router = useRouter();
  const [preferenceCount,setPreferenceCount] = useState(0);
  const [progressBar,setProgressBar] = useState(0.25);

  return (
    <View style={styles.container}>
      <View style={styles.backAndProgressBarWrapper}>
        {/* Back Button */}
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Image
            source={require("../../assets/images/back.png")}
            style={styles.backIcon}
          />
        </TouchableOpacity>

        {/* Progress Bar */}
        <Progress.Bar
          progress={progressBar}
          width={220} 
          style={styles.progressBar}
          color="rgba(38, 170, 82, 1)"
          borderColor="#e7e7e7"
          height={17}
          borderRadius={30}
          unfilledColor="#ccc"
        />
      </View>
      <View style={styles.travelPreferencesTitleAndDescriptionWrapper}>
        <View style={styles.travelPreferencesTitleWrapper}>
         <Text style={styles.travelPreferencesTitle}>
         Travel Preferences ✈️
         </Text>
        </View>
         <View style={styles.travelPreferencesDescriptionWrapper}>
         <Text style={styles.travelPreferencesDescription}>
          Tell us your travel preferences and we'll tailor recommendations to your style. Don't worry,you can always change it later in the settings.
         </Text>
        </View>
      </View>

      <View style={styles.preferencesContainer}>
      {/* <TouchableOpacity style={styles.preferenceItem}>
        <Text style={styles.preferenceItemText}>
        Historical Sites 🏺
        </Text>
      </TouchableOpacity> */}
      <PreferenceItem title="Historical Sites 🏺" onPress={()=>console.log("Pressed")} key={1} />
      <PreferenceItem title="City Breaks 🌇" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title="Religious Tourism ✝️☪️✡️" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title="Glamping ⛺" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title="Beach Vacations 🏖️" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title=" Nature Escapes🌿" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title="Festivals & Events 🎉" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title="Road Trips 🚗" onPress={()=>console.log("Pressed")} />
      <PreferenceItem title="Food Tourism 🍔" onPress={()=>console.log("Pressed")}  />
      <PreferenceItem title="Backpacking 🎒" onPress={()=>console.log("Pressed")}  />
      <PreferenceItem title="Cruise Vacations 🛥️" onPress={()=>console.log("Pressed")}  />
      <PreferenceItem title=" Art Galleries 🎨" onPress={()=>console.log("Pressed")}  />
      <PreferenceItem title="Cultural Exploration 🏛️" onPress={()=>console.log("Pressed")}  />
      </View>

      <TouchableOpacity style={{width:"90%",borderRadius:20,backgroundColor:"#3CB371",justifyContent:"center",alignItems:"center",margin:"auto",padding:14}}
      onPress={()=>{setProgressBar(progressBar+0.25)}}
      
      >
        <Text style={{fontFamily:"Poppins-Medium",color:"white",fontSize:17}}>
            Continue ({preferenceCount}/5)
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default TravelPreferences;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 80,
    backgroundColor: "#fff",
  },
  backAndProgressBarWrapper: {
    flexDirection: "row",
    alignItems: "center",
    gap:20,
  },
  backButton: {
    backgroundColor: "#e6e1e1ff",
    borderRadius: 20,
    padding: 5,
    marginRight: 15,
  },
  backIcon: {
    width: 25,
    height: 25,
    resizeMode: "contain",
  },
  travelPreferencesTitleAndDescriptionWrapper:{
    flexDirection:"column",
    gap:12,
    marginTop:50,
  },
  travelPreferencesTitle:{
    fontSize:30,
    fontFamily:"Poppins-SemiBold",
  },
  travelPreferencesDescription:{
    fontSize:14,
    fontFamily:"Poppins-Regular",
    color:"rgba(102, 98, 98, 1)",
  },
  preferencesContainer:{
    flexDirection:"row",
    gap:14,
    marginTop:10,
    height:"auto",
     flexWrap: "wrap",   
  },
});
