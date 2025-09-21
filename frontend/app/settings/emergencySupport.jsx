import { StyleSheet, Text, View,Style,TouchableOpacity,Image } from 'react-native'
import React from 'react'
import { router } from 'expo-router'

const Emergency = () => {
  return (
    <View style={styles.container}>
     <View style={styles.backAndPersonalInfoTitle}>
             <TouchableOpacity onPress={() => router.back()}>
               <Image
                 source={require("../../assets/images/back.png")}
                 style={{ width: 30, height: 30 }}
               />
             </TouchableOpacity>
             <Text
               style={{
                 fontFamily: "Poppins-SemiBold",
                 fontSize: 20,
                 color: "#000000ff",
                 margin: "auto",
               }}
             >
               Emergency Contact
             </Text>
           </View>

           <View style ={styles.emergencyWrapper}>
            <View style={styles.emergencyItem}>
             <Image
                source={require("../../assets/images/policeman.png")}
                style={{ width: 100, height: 100 }}
             />
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:18}}>Police</Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:16}}>122</Text>
            </View>

            <View style={styles.emergencyItem}>
               <Image
                source={require("../../assets/images/ambulance.png")}
                style={{ width: 100, height: 100 }}
             />
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:18}}>Ambulance</Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:16}}>123</Text>
            </View>

            <View style={styles.emergencyItem}>
               <Image
                source={require("../../assets/images/fire-station.png")}
                style={{ width: 100, height: 100 }}
             />
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:18}}>Fire Dept.</Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:16}}>180</Text>
            </View>
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
    backgroundColor:"#fff",
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