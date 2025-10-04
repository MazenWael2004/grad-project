import { StyleSheet, Text, View,Image,TouchableOpacity } from 'react-native'
import React from 'react'
import LottieView from 'lottie-react-native';
import {useRouter} from 'expo-router';


const PaymentCompleted = () => {
  const router=useRouter();
  return (
    <View style={styles.container}>
      <LottieView
        source={require('../../assets/images/Payment Success.json')}
        autoPlay
        style={{width:200,height:200}}
        onAnimationFinish={router.push("main/settings")}
      />
      <Text style={styles.title}>
        Payment Completed!
      </Text>
    </View>
  )
}

export default PaymentCompleted;

const styles = StyleSheet.create({
  container:{
    flex:1,
    flexDirection:"column",
    gap:5,
    justifyContent:"center",
    alignItems:"center",
    backgroundColor:"white"
  },
  title:{
    fontSize:30,
    fontFamily:"Poppins-SemiBold",
  },
  description:{
    fontFamily:"Poppins-Regular",
    textAlign:"center",
    fontSize:16,
    height:100,
    color:"rgba(102, 98, 98, 1)",
  }
})