import { StyleSheet, Text, View } from 'react-native'
import { useEffect, useRef,useContext } from "react";
import LottieView from 'lottie-react-native';
import { ThemeContext } from "../../theme/ThemeContext";
import {LIGHT_THEME,DARK_THEME} from '../../constants/themes'
import { router } from 'expo-router';


const GeneratingTripLoader = () => {
    const {theme} = useContext(ThemeContext);
    const currentTheme = theme === "Light"?LIGHT_THEME:DARK_THEME;
    const handleAnimationFinish = () => {
    setTimeout(() => {
      router.push("main/myTrips");
    }, 4000);
  };

  useEffect(()=>{
    handleAnimationFinish();
  },[]);

  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
         <LottieView
        source={require('../../assets/images/trip.json')}
        autoPlay
        loop={true}
        speed={1.5}
        onAnimationFinish={handleAnimationFinish}
        style={{ width: 300, height: 300}}
      />
      <Text style={{fontFamily:"Poppins-SemiBold",fontSize:26,color:currentTheme.text}}>
        Generating Itinerary
      </Text>

       <Text style={{fontFamily:"Poppins-Medium",fontSize:15,color:currentTheme.description}}>
        Please Wait...
      </Text>
    </View>
  )
}

export default GeneratingTripLoader

const styles = StyleSheet.create({
container:{
    flex:1,
    justifyContent:"center",
    alignItems:"center",
    flexDirection:'column',
}
})