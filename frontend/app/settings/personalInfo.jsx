import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  TextInput,
  ScrollView
} from "react-native";
import {useState,useRef,useContext} from "react";
import { router } from "expo-router";
import PhoneInput from "react-native-phone-number-input";
import { ThemeContext } from "../../theme/ThemeContext";
import { useUser } from "../contexts/userContext";
import * as ImagePicker from "expo-image-picker";
import { LIGHT_THEME,DARK_THEME } from "../../constants/themes";



const PersonalInfo = () => {
  const {theme} = useContext(ThemeContext);
  const [image, setImage] = useState(null);
  const {user, setUser} = useUser();
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const [value, setValue] = useState("");
  const [fullName, setFullName] = useState("Mazen Wael");
  console.log("User from context: ", JSON.stringify(user, null, 2)); // Debug log to check user data from context

  const [formattedValue, setFormattedValue] = useState("");  // Formatted Phone Number
  const [valid, setValid] = useState(false);
  const [showMessage, setShowMessage] = useState(false);


  const handleSaveChanges = () =>{

    console.log("Phone Number: "+formattedValue);
  }

   const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.canceled) { 
      setImage(result.assets[0].uri);
      setUser(prevUser => ({
        ...prevUser,
        profilePic: result.assets[0].uri,
      }));
      
    }
  };

  


  return (
    <View style={[styles.container,{backgroundColor:currentTheme.background}]}>
        <ScrollView showsVerticalScrollIndicator={false}>
      <View style={styles.backAndPersonalInfoTitle}>
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 30, height: 30,tintColor:currentTheme.iconColor }}
          />
        </TouchableOpacity>
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: currentTheme.text,
            margin: "auto",
          }}
        >
          Personal Info
        </Text>
      </View>
      <View style={styles.profilePictureWrapper}>
         {user.profilePic?(
        <Image
          source={{ uri: user.profilePic }}
          style={styles.profilePicture}
        />
      ):(
        <View style={styles.profilePicture} />
        
      )}
        <TouchableOpacity

          style={{
            backgroundColor: currentTheme.searchBackground,
            paddingHorizontal: 10,
            paddingVertical: 5,
            borderRadius: 10,
            marginTop: 10,
            marginBottom: 20,
          }}
          onPress={pickImage}
        >
          <Text style={{ fontFamily: "Poppins-Medium", color: currentTheme.text }}>
            Change Profile Picture
          </Text>
        </TouchableOpacity>
      </View>
      <View style={styles.formWrapper}>
        <View style={styles.inputWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 16,
              color: currentTheme.text,
            }}
          >
            Full Name
            
          </Text>
          <View>
            <TextInput
            value="Mazen Wael"
              style={[
                {
                  height: 50,
                  backgroundColor: currentTheme.searchBackground,
                  color:currentTheme.text,
                  paddingHorizontal: 10,
                  borderRadius: 10,
                  marginBottom: 2,
                  fontFamily: "Poppins-Medium",
                  position: "relative",
                },
              ]}
            />
          </View>
        </View>

            <View style={styles.inputWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 16,
              color: currentTheme.text,
            }}
          >
            E-mail
            
          </Text>
          <View>
            <TextInput
            value="random-email@gmail.com"
              style={[
                {
                  height: 50,
                  backgroundColor: currentTheme.searchBackground,
                  color: currentTheme.text,
                  paddingHorizontal: 10,
                  borderRadius: 10,
                  marginBottom: 2,
                  fontFamily: "Poppins-Medium",
                  position: "relative",
                },
              ]}
            />
          </View>
        </View>

            <View style={styles.inputWrapper}>
          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              fontSize: 16,
              color: currentTheme.text,
            }}
          >
            Phone Number
            
          </Text>
          {/* <View>
            <TextInput
            value="Mazen Wael"
              style={[
                {
                  height: 50,
                  backgroundColor: "#e9e7e7ff",
                  paddingHorizontal: 10,
                  borderRadius: 10,
                  marginBottom: 2,
                  fontFamily: "Poppins-Medium",
                  position: "relative",
                },
              ]}
            />
          </View> */}
           <PhoneInput
            defaultValue={value}
            defaultCode="DM"
            layout="first"
            onChangeText={(text) => {
              setValue(text);
              console.log("Phone Number: "+text);
            }}
            onChangeFormattedText={(text) => {
              setFormattedValue(text);
            }}
            withDarkTheme
            withShadow
            textInputStyle={{
                  fontFamily: "Poppins-Medium",

            }}
            codeTextStyle={{
               fontFamily: "Poppins-Medium", 
            }}
            containerStyle={{
                 backgroundColor: currentTheme.searchBackground,
                  paddingHorizontal: 10,
                  borderRadius: 10,
                  marginBottom: 2,
                  fontFamily: "Poppins-Medium",
                  position: "relative",
                  width:"100%"
                
            }}
            countryPickerButtonStyle={{
                fontFamily:"Poppins-SemiBold",
            }}
          />
          
        </View>
      </View>
      </ScrollView>
          
      <TouchableOpacity style={{borderRadius:30,backgroundColor:"#D4AF37",width:"100%",justifyContent:"center",alignItems:"center",padding:12,marginBottom:40,}} onPress={handleSaveChanges}>
        <Text style={{fontFamily:"Poppins-Medium",color:"white",fontSize:15}}>
          Save Changes
        </Text>
      </TouchableOpacity>

    </View>
  );
};

export default PersonalInfo;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "column",
  },
  backAndPersonalInfoTitle: {
    flexDirection: "row",
    alignItems: "center",
    width: "90%",
    marginBottom: 15,
  },
  profilePictureWrapper: {
    width: "100%",
    height: 150,
    justifyContent: "center",
    alignItems: "center",
  },
  profilePicture: {
    backgroundColor: "grey",
    borderRadius: 100,
    height: 120,
    width: 120,
  },
  formWrapper: {
    flexDirection: "column",
    gap: 10,
    width: "100%",
  },
  inputWrapper: {
    marginBottom: 5,
  },
});
