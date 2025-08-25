import { StyleSheet, Text, View,TouchableOpacity } from 'react-native'
import React from 'react'

const PreferenceItem = (props) => {
  return (
    <TouchableOpacity style={[styles.preferenceItem,props.isSelected && styles.selected]} onPress={props.onPress}>
            <Text style={[styles.preferenceItemText,props.isSelected && styles.selectedText]}>
             {props.title}
            </Text>
  </TouchableOpacity>
  )
}

export default PreferenceItem

const styles = StyleSheet.create({
    preferenceItem:{
    borderWidth:1,
    width:"auto",
    paddingHorizontal:11,
    paddingVertical:5,
    borderRadius:20,

  },

  preferenceItemText:{
    fontFamily:"Poppins-Medium",
    fontSize:12.5,
  },
   selected: {
    backgroundColor: "#FFA500",
    borderColor: "#FFA500",
  },
  selectedText: {
    color: "#fff",
  },
})