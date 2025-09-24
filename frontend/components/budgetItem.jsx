import { StyleSheet, Text, TouchableOpacity } from "react-native";
import { useContext } from "react";
import { ThemeContext } from "../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../constants/themes";

const BudgetItem = (props) => {
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  return (
    <TouchableOpacity
      style={[{
        borderWidth: 1,
        borderColor: "#dcdbd9ff",
        padding: 15,
        borderRadius: 10,
        width: "100%",
        flexDirection: "column",
        justifyContent: "center",
        marginBottom:15,
      },
      props.isSelected && styles.selectedStyle
    ]}
    onPress={props.onPress}
    >
      <Text
        style={{
          fontFamily: "Poppins-SemiBold",
          fontSize: 16,
          color: currentTheme.text,
        }}
      >
        {props.title}
      </Text>
      <Text
        style={{
          fontFamily: "Poppins-Regular",
          fontSize: 14,
          color: currentTheme.description,
        }}
      >
        {props.description}
      </Text>
    </TouchableOpacity>
  );
};

export default BudgetItem;

const styles = StyleSheet.create({
     selectedStyle:{
     borderColor: "#D4AF37",
  }
});
