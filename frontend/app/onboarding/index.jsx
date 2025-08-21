import { Text, View, TouchableOpacity, Image, Dimensions,TextInput } from "react-native";
import { useState } from "react";
import AppIntroSlider from "react-native-app-intro-slider";
import { useFonts } from "expo-font";
import { useRouter } from "expo-router";

export default function Index() {
  const [fontsLoaded] = useFonts({
    "Poppins-Bold": require("../../assets/fonts/Poppins/Poppins-Bold.ttf"),
    "Poppins-Medium": require("../../assets/fonts/Poppins/Poppins-Medium.ttf"),
    "Poppins-Light": require("../../assets/fonts/Poppins/Poppins-Light.ttf"),
    "Poppins-Regular": require("../../assets/fonts/Poppins/Poppins-Regular.ttf"),
    "Poppins-SemiBold": require("../../assets/fonts/Poppins/Poppins-SemiBold.ttf"),
    "Poppins-ExtraBold": require("../../assets/fonts/Poppins/Poppins-ExtraBold.ttf"),
  });

  const [showHomeScreen, setShowHomeScreen] = useState(false);
  const router = useRouter();
  const slides = [
    {
      key: "1",
      title: "Intelligent Trip Planning with Historai",
      text: "Let our AI plan a detailed trip to your preferences. Easy planning for your unforgettable experience.",
      image: require("../../assets/images/choosing-travelling.jpg"),
    },
    {
      key: "2",
      title: "AI Tour Guide",
      text: "Learn the stories behind Egypt’s monuments and treasures with AI-powered answers to your questions.",
      image: require("../../assets/images/Chatbot.jpg"),
    },
    {
      key: "3",
      title: "Get Started",
      text: "Embark on your adventure through Egypt’s timeless heritage — let’s begin!",
      image: require("../../assets/images/Pyramids.jpg"),
    },
  ];
   

  const buttonLabel = (text) => {
    return (
      <View
        style={{
          paddingVertical: 10,
          paddingHorizontal: 25,
          backgroundColor: "rgba(201, 124, 29, 1)",
          borderRadius: 25,
        }}
      >
        <Text
          style={{
            color: "#fff",
            fontSize: 16,
            fontFamily: "Poppins-Medium",
          }}
        >
          {text}
        </Text>
      </View>
    );
  };

    if (!fontsLoaded) {
    return null; 
    }

  if (!showHomeScreen) {
    return (
      <AppIntroSlider
        data={slides}
        renderItem={({ item }) => (
          <View
            style={{
              flex: 1,
              justifyContent: "center",
              alignItems: "center",
              padding: 20,
              backgroundColor: "#fff",
            }}
          >
            {item.image && (
              <Image
                source={item.image}
                style={{
                  width: Dimensions.get("window").width * 0.9,
                  height: 350,
                  resizeMode: "contain",
                }}
              />
            )}
            <Text
              style={{
                fontSize: 28,
                fontFamily: "Poppins-SemiBold",
                textAlign: "center",
                color: "rgba(33, 33, 33, 1)",
                marginBottom: 15,
              }}
            >
              {item.title}
            </Text>
            <Text
              style={{
                fontSize: 16,
                fontFamily: "Poppins-Regular",
                color: "rgba(102, 98, 98, 1)",
                textAlign: "center",
                paddingHorizontal: 20,
                lineHeight: 22,
              }}
            >
              {item.text}
            </Text>
          </View>
        )}
        activeDotStyle={{
          backgroundColor: "rgba(201, 124, 29, 1)",
          width: 30,
        }}
        dotStyle={{
          backgroundColor: "rgba(201, 124, 29, 0.3)",
        }}
        onDone={() => {router.push("/authentication/login")}}
        renderDoneButton={() => buttonLabel("Get Started")}
        renderNextButton={() => buttonLabel("Next")}
      />
    );
  }


}

