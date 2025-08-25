import { Text, View, StyleSheet, Image, Animated } from "react-native";
import { useEffect, useRef } from "react";
import { useRouter } from "expo-router";
import { useFonts } from "expo-font";
import LottieView from 'lottie-react-native';

export default function Index() {
  const router = useRouter();

  const [fontsLoaded] = useFonts({
    "Poppins-Bold": require("../assets/fonts/Poppins/Poppins-Bold.ttf"),
    "Poppins-Medium": require("../assets/fonts/Poppins/Poppins-Medium.ttf"),
    "Poppins-Light": require("../assets/fonts/Poppins/Poppins-Light.ttf"),
    "Poppins-Regular": require("../assets/fonts/Poppins/Poppins-Regular.ttf"),
    "Poppins-SemiBold": require("../assets/fonts/Poppins/Poppins-SemiBold.ttf"),
    "Poppins-ExtraBold": require("../assets/fonts/Poppins/Poppins-ExtraBold.ttf"),
  });

  




  const handleAnimationFinish = () => {
    setTimeout(() => {
      router.push("/onboarding");
    }, 4000);
  };

  useEffect(() => {
    handleAnimationFinish();
  }, []);

    if (!fontsLoaded) {
    return <View style={{ flex: 1, backgroundColor: "#D2691E" }} />; 
    // return a fallback view instead of null
  }

  return (
    <View style={styles.container}>
      <Image
        source={require("../assets/images/Pyramids.png")}
        style={styles.menuAppImage}
      />
      <Text style={{
        fontFamily: "Poppins-ExtraBold",
        fontSize: 30,
        color: "#fff",
        marginTop: 20
      }}>
        Historai
      </Text>

      <LottieView
        source={require('../assets/images/loading.json')}
        autoPlay
        loop={false}
        speed={1.5}
        onAnimationFinish={handleAnimationFinish}
        style={{ width: 150, height: 150, position: "absolute", bottom: 50 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    flexDirection:"column",
    backgroundColor:"#D2691E"
  },
  menuAppWrapper: {
    backgroundColor: "orange",
    width: 150,
    height: 150,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 100,
  },
  menuAppImage: {
    width: 200,
    height: 200,
    borderRadius: 50,
    resizeMode: "cover",
  
  },
});
