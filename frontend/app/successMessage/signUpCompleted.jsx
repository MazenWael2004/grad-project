import { StyleSheet, Text, View,Image,TouchableOpacity } from 'react-native'
import React from 'react'
import LottieView from 'lottie-react-native';
import {useRouter} from 'expo-router';


const SignUpCompleted = () => {
  const router=useRouter();
  return (
    <View style={styles.container}>
      <LottieView
        source={require('../../assets/images/Success Check.json')}
        autoPlay
        loop={false}
        style={{width:200,height:200}}
      />
      <Text style={styles.title}>
        You're all set!
      </Text>
      <Text style={styles.description}>
        Congratulations,You're now part of the Historai community. Your personalized travel experiences and AI-powered tour guide await.
      </Text>

      <TouchableOpacity style={{width:"90%",borderRadius:50,backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",padding:14,position:"absolute",top:760}}
      onPress={()=>router.push('/main')}
            
      >
       <Text style={{fontFamily:"Poppins-Medium",color:"white",fontSize:17}}>
         Explore Egypt
       </Text>
     </TouchableOpacity>
      
    </View>
  )
}

export default SignUpCompleted

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