import { Text, View, StyleSheet, Image, Animated } from "react-native";
import { useEffect, useRef } from "react";
import { useRouter } from "expo-router";

export default function Index() {
  const paddingAnimation = useRef(new Animated.Value(10)).current;
  const router = useRouter();

  useEffect(() => {
    Animated.timing(paddingAnimation, {
      toValue: 1000,
      duration: 1500,
      useNativeDriver: false,
    }).start(()=>{
      router.push("/onboarding");
    });
  }, []);

  return (
    <View style={styles.container}>
      <Animated.View
        style={[styles.menuAppWrapper, { padding: paddingAnimation }]}
      >
        <Image
          source={require("../assets/images/Group 1.png")}
          style={styles.menuAppImage}
        />
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
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
    borderWidth: 5,
  },
});
