import { StyleSheet, Text, View, Image,TouchableOpacity } from "react-native";
import React from "react";
import { router } from "expo-router";

const Settings = () => {
  return (
    <View style={styles.container}>
      <View style={styles.logoAndSettingsTitle}>
        <Image
          source={require("../../assets/images/Pyramids.png")}
          style={{ width: 55, height: 55, resizeMode: "contain" }}
        />
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: "#000000ff",
            margin: "auto",
          }}
        >
          Settings
        </Text>
      </View>

      <TouchableOpacity style={styles.upgradePlanWrapper} onPress={()=> router.push("plans/plans")}>
      <Image
       source={require("../../assets/images/badge.png")}
       style={{width:55,height:55}}
       />
       <View style={{flexDirection:"column"}}>
       <Text style={{fontFamily:"Poppins-SemiBold",color:"white"}}>
        Upgrade Plan to Unlock More!
       </Text>
       <Text style={{fontFamily:"Poppins-Regular",color:"white",fontSize:8}}>
        Enjoy all benefits and explore more possibilities
       </Text>
       </View>
       <Image
       source={require("../../assets/images/right-arrow.png")}
       style={{width:20,height:20}}
       />

      </TouchableOpacity>

      <View style={styles.acutalSettingsWrapper}>
         <TouchableOpacity style={styles.settingItem} onPress={()=>router.push("settings/personalInfo")}>
          <Image
          source={require("../../assets/images/user.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           Personal Info
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
          <Image
          source={require("../../assets/images/crown.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           Billing & Subscriptions
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
          <Image
          source={require("../../assets/images/security.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           Account & Security
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>

         <TouchableOpacity style={styles.settingItem}>
          <Image
          source={require("../../assets/images/exchange.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           Live Currency Converter
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>

         <TouchableOpacity style={styles.settingItem} onPress={()=>{router.push("settings/paymentMethods")}}>
          <Image
          source={require("../../assets/images/credit-card.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           Payment Methods
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem} onPress={()=>{router.push("settings/emergencySupport")}}>
          <Image
          source={require("../../assets/images/call.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           Emergency Support
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
          <Image
          source={require("../../assets/images/eye.png")}
          style={{width:25,height:25}}
          />
          <Text style={{fontFamily:"Poppins-SemiBold",fontSize:15}}>
           App Appearance 
          </Text>
          <Image
          source={require("../../assets/images/right-arrow.png")}
          style={{width:25,height:25,position:"absolute",right:1}}
          />

         </TouchableOpacity>
      </View>
    </View>
  );
};

export default Settings;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "column",
  },
  logoAndSettingsTitle:{
    flexDirection: "row",
    alignItems: "center",
    width: "82%",
    marginBottom:15,
  },
  upgradePlanWrapper:{
    padding:10,
    width:"100%",
    height:100,
    backgroundColor:"#D4AF37",
    borderRadius:10,
    flexDirection:"row",
    justifyContent:"space-between",
    alignItems:"center",
    marginBottom:20,
  },
  acutalSettingsWrapper:{
    flexDirection:"column",
    gap:30,
  },
  
  settingItem:{
    flexDirection:"row",
    alignItems:"center",
    gap:15,
    position:"relative",
  }
});
