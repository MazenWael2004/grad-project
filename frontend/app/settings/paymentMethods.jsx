import { StyleSheet, Text, View,TouchableOpacity,Image } from 'react-native'
import { router } from "expo-router";
import React,{useState} from 'react'

const PaymentMethods = () => {
    const [isPaymentMethodExists,setIsPaymentMethodExists] = useState(false);
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
                Payment Methods
              </Text>
            </View>
            {!isPaymentMethodExists && (
                <View style={styles.noPaymentAddedContainer}>
                     <Image
                     source={require("../../assets/images/add-payment.jpg")}
                     style={{width:250,height:250}}
                     />
                     <Text style={{fontSize:26,fontFamily:"Poppins-SemiBold",textAlign:"center"}}>
                      No Payment Method Added.
                     </Text>

                     <TouchableOpacity style={{backgroundColor:"#ffffffff",borderColor:"#D4AF37",borderWidth:1,justifyContent:"center",alignItems:"center",padding:20,borderRadius:35,}} onPress={()=>{router.push("addPaymentMethod")}}>
                      <Text style={{fontFamily:"Poppins-SemiBold",color:"#D4AF37",width:"100%"}}>Add Payment Method</Text>
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
    backgroundColor:"#fff",
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