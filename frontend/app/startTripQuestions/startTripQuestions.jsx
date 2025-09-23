import { StyleSheet, Text, View, TouchableOpacity, Image } from "react-native";
import React, { useState } from "react";
import * as Progress from "react-native-progress";
import { router } from "expo-router";

const StartTripQuestions = () => {
  const [progressBar, setProgressBar] = useState(0.25);

  const getStepTitle = (progressBar) => {
    if (progressBar === 0.25) return "Who is going? 🧳";
    if (progressBar === 0.5) return "When will your adventure begin and end? 📅";
    if (progressBar === 0.75) return "Tailor your trip to your tastes ✨";
    if (progressBar === 1) return "Set your trip budget 💰";
    return "";
    };
  return (
    <View style={styles.container}>
      <View style={styles.backAndProgressBarWrapper}>
        {/* Back Button */}
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 30, height: 30 }}
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

      <Text style={{fontFamily:"Poppins-SemiBold",fontSize:30,marginBottom:10}}>{getStepTitle(progressBar)}</Text>
      <Text style={{fontFamily:"Poppins-Regular",fontSize:16,marginBottom:20,color:"#666"}}>Let&apos;s start with the basics. Who&apos;s joining you on this adventure?</Text>
        <View style={{flexDirection:"column",gap:15}}>
            <TouchableOpacity style={{borderWidth:1,borderColor:"#dcdbd9ff",padding:15,borderRadius:10,width:"100%",flexDirection:"column",justifyContent:"center",gap:5,}}>
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:16}}>Only Me 🚶</Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:14,color:"#666"}}>Travelling solo, just you.</Text>
            </TouchableOpacity>

            <TouchableOpacity style={{borderWidth:1,borderColor:"#dcdbd9ff",padding:15,borderRadius:10,width:"100%",flexDirection:"column",justifyContent:"center",gap:5,}}>
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:16}}>Spouse ❤️</Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:14,color:"#666"}}>A romantic adventure for you and your wife.</Text>
            </TouchableOpacity>

            <TouchableOpacity style={{borderWidth:1,borderColor:"#dcdbd9ff",padding:15,borderRadius:10,width:"100%",flexDirection:"column",justifyContent:"center",gap:5,}}>
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:16}}>Family 👨‍👩‍👧 </Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:14,color:"#666"}}>Quality time with your closest ones.</Text>
            </TouchableOpacity>

            <TouchableOpacity style={{borderWidth:1,borderColor:"#dcdbd9ff",padding:15,borderRadius:10,width:"100%",flexDirection:"column",justifyContent:"center",gap:5,}}>
                <Text style={{fontFamily:"Poppins-SemiBold",fontSize:16}}>Friends 🤝</Text>
                <Text style={{fontFamily:"Poppins-Regular",fontSize:14,color:"#666"}}>Fun time with your pals.</Text>
            </TouchableOpacity>
        </View>
        <TouchableOpacity style={{borderRadius:20,backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",position:"absolute",bottom:30,left:20,right:20,padding:14,margin:"auto"}}
        onPress={()=>{setProgressBar((prev)=>prev + 0.25)}}
        >
        <Text style={{fontFamily:"Poppins-Medium",color:"white",fontSize:17}}>
            Continue
        </Text>
        </TouchableOpacity>


    </View>
  );
};

export default StartTripQuestions;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: "column",
    paddingTop: 70,
    paddingHorizontal: 30,
    position: "relative",
  },
  backAndProgressBarWrapper: {
    flexDirection: "row",
    alignItems: "center",
    width: "100%",
    marginBottom: 55,
  },

  progressBar: {
    marginLeft: 30,
  },
});
