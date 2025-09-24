import { StyleSheet, Text,TouchableOpacity } from 'react-native'
import React,{useContext} from 'react'
import { ThemeContext } from "../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../constants/themes";

const PreferenceItem = (props) => {
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  return (
    <TouchableOpacity style={[styles.preferenceItem,props.isSelected && styles.selected,{borderColor:currentTheme.description}]} onPress={props.onPress}>
            <Text style={[styles.preferenceItemText,{color:currentTheme.text},props.isSelected && styles.selectedText]}>
             {props.title}
            </Text>
  </TouchableOpacity>
  )
}

export default PreferenceItem

const styles = StyleSheet.create({
    preferenceItem:{
    borderWidth:0.45,
    width:"auto",
    paddingHorizontal:11,
    paddingVertical:5,
    borderRadius:20,
  

  },

  preferenceItemText:{
    fontFamily:"Poppins-SemiBold",
    fontSize:13,
  },
   selected: {
    backgroundColor: "#FFA500",
    borderColor: "#FFA500",
  },
  selectedText: {
    color: "#fff",
  },
})