import { StyleSheet, Text, View, TouchableOpacity, Image } from "react-native";
import { useContext } from "react";
import { ThemeContext } from "../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../constants/themes";

const EmergencyItem = (props) => {
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  return (
    <View
      style={[
        styles.emergencyItem,
        { backgroundColor: currentTheme.searchBackground },
      ]}
    >
      <Image
        source={props.image}
        style={{ width: 100, height: 100 }}
      />
      <Text
        style={{
          fontFamily: "Poppins-SemiBold",
          fontSize: 18,
          color: currentTheme.text,
        }}
      >
        {props.name}
      </Text>
      <Text
        style={{
          fontFamily: "Poppins-Regular",
          fontSize: 16,
          color: currentTheme.text,
        }}
      >
        {props.contact}
      </Text>
    </View>
  );
};

export default EmergencyItem;

const styles = StyleSheet.create({
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
});
