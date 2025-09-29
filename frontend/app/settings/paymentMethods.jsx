import { StyleSheet, Text, View,TouchableOpacity,Image } from 'react-native'
import { router } from "expo-router";
import React,{useState,useContext} from 'react'
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME,DARK_THEME } from "../../constants/themes";


const PaymentMethods = () => {
    const [isPaymentMethodExists,setIsPaymentMethodExists] = useState(false);
    const {theme} = useContext(ThemeContext);
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
                Payment Methods
              </Text>
            </View>
            {!isPaymentMethodExists && (
                <View style={styles.noPaymentAddedContainer}>
                     <Image
                     source={require("../../assets/images/payment-method.png")}
                     style={{width:160,height:160,tintColor:currentTheme.description}}
                     />
                     <Text style={{fontSize:26,fontFamily:"Poppins-SemiBold",textAlign:"center",color:currentTheme.text}}>
                      No Payment Method Added.
                     </Text>

                     <TouchableOpacity style={{backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",padding:20,borderRadius:35,}} onPress={()=>{router.push("addPaymentMethod")}}>
                      <Text style={{fontFamily:"Poppins-SemiBold",color:"white",width:"100%"}}>Add Payment Method</Text>
                     </TouchableOpacity>
                </View>
            )}
    </View>
  )
}

export default PaymentMethods

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
  noPaymentAddedContainer:{

    height:"85%",
    flexDirection:"column",
    gap:10,
    justifyContent:"center",
    alignItems:"center",
  }
})