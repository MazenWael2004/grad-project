import { StyleSheet, Text, View,TouchableOpacity,Image } from 'react-native'
import {useContext} from 'react'
import { router } from 'expo-router'
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import emergencies from '../../constants/emergencies';
import EmergencyItem from '../../components/emergencyItem';

const Emergency = () => {
   const { theme } = useContext(ThemeContext);
   const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
     <View style={styles.backAndPersonalInfoTitle}>
             <TouchableOpacity onPress={() => router.back()}>
               <Image
                 source={require("../../assets/images/back.png")}
                 style={{ width: 30, height: 30,tintColor:currentTheme.iconColor }}
               />
             </TouchableOpacity>
             <Text
               style={{
                 fontFamily: "Poppins-SemiBold",
                 fontSize: 20,
                 color: currentTheme.text,
                 margin: "auto",
               }}
             >
               Emergency Contact
             </Text>
           </View>

           <View style ={styles.emergencyWrapper}>
            {emergencies.map((item)=>{
              return(
                <EmergencyItem key={item.id} name={item.name} image={item.image} contact={item.contact} />
              )
            })}
           </View>
    </View>
  )
}

export default Emergency

const styles = StyleSheet.create({
    container: {
    flex: 1,
    paddingTop: 70, 
    paddingHorizontal: 30,
    flexDirection: "column",
    // backgroundColor:"#fff",
    },
     backAndPersonalInfoTitle: {
    flexDirection: "row",
    alignItems: "center",
    width: "90%",
    marginBottom: 15,
  },
  emergencyWrapper:{
    flex:1,
    justifyContent:"space-around",
    alignItems:"center",
    flexDirection:"column",

  },
  emergencyItem:{
    width:200,
    height:200,
    backgroundColor:"#e9e6e6ff",
    borderRadius:10,
    justifyContent:"center",
    alignItems:"center",
    flexDirection:"column",
    gap:10,
  }
})