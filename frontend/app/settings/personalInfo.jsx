import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  TextInput,
  ScrollView,
} from "react-native";
import { useState, useContext } from "react"; // removed unused useRef
import { router } from "expo-router";
import PhoneInput from "react-native-phone-number-input";
import { ThemeContext } from "../../theme/ThemeContext";
import { useUser } from "../contexts/userContext";
import * as ImagePicker from "expo-image-picker";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import api from "../../src/services/api";
import Constants from "expo-constants";
const { API_BASE_URL } = Constants.expoConfig.extra;

const PersonalInfo = () => {
  const { theme } = useContext(ThemeContext);
  const { user, setUser } = useUser();

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  const [image, setImage] = useState(null);
  const [firstName,setFirstName] = useState(user.first_name || "");
  const [lastName,setLastName] = useState(user.last_name || "");
  const [fullName, setFullName] = useState(user.name || "");
  const [phoneValue, setPhoneValue] = useState(user.phoneNumber || ""); 
  const [formattedValue, setFormattedValue] = useState("");
  const profilePicUri = image || user.profilePic;

const handleSaveChanges = async () => {
  // const updatedUser = {
  //   ...user,
  //   first_name: firstName,
  //   phoneNumber: formattedValue + phoneValue,
  //   profilePic: image || user.profilePic,
  // };

  // setUser(updatedUser);

  try {
    const response = await api.patch(
      `${API_BASE_URL}/api/accounts/profile/update/`,
      {
        first_name: firstName,
        last_name: lastName,
        phone_number: formattedValue,
      },
      {
        headers: {
          Authorization: `Bearer ${user.access}`,
        },
      }
    );

    const userData = response.data.user; // IMPORTANT

    // correct way to update state
    setUser((prev) => ({
      ...prev,
      ...userData,
    }));

  } catch (error) {
    console.error(error.response?.data || error.message);
  }
};
  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });
    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: currentTheme.background }]}>
      <ScrollView showsVerticalScrollIndicator={false}>

        {/* Header */}
        <View style={styles.backAndPersonalInfoTitle}>
          <TouchableOpacity onPress={() => router.back()}>
            <Image
              source={require("../../assets/images/back.png")}
              style={{ width: 30, height: 30, tintColor: currentTheme.iconColor }}
            />
          </TouchableOpacity>
          {/* FIX: replaced invalid margin:"auto" with flex:1 + textAlign:"center" */}
          <Text style={[styles.headerTitle, { color: currentTheme.text }]}>
            Personal Info
          </Text>
        </View>

        {/* Profile Picture */}
        <View style={styles.profilePictureWrapper}>
          {/* FIX: profilePicUri reflects newly picked image immediately */}
          {/* {profilePicUri ? (
            <Image source={{ uri: profilePicUri }} style={styles.profilePicture} />
          ) : (
            <View style={styles.profilePicture} />
          )} */}
           <Image source={require("../../assets/images/avatar.png")} style={styles.profilePicture} />
          {/* <TouchableOpacity
            style={[styles.changePicButton, { backgroundColor: currentTheme.searchBackground }]}
            onPress={pickImage}
          >
            <Text style={{ fontFamily: "Poppins-Medium", color: currentTheme.text }}>
              Change Profile Picture
            </Text>
          </TouchableOpacity> */}
        </View>

        {/* Form */}
        <View style={styles.formWrapper}>

          {/* First Name — FIX: added onChangeText so edits are captured */}
          <View style={styles.inputWrapper}>
            <Text style={[styles.inputLabel, { color: currentTheme.text }]}>First Name</Text>
            <TextInput
              value={firstName}
              onChangeText={setFirstName}
              style={[styles.textInput, {
                backgroundColor: currentTheme.searchBackground,
                color: currentTheme.text,
              }]}
            />
          </View>

           {/* Last Name — FIX: added onChangeText so edits are captured */}
          <View style={styles.inputWrapper}>
            <Text style={[styles.inputLabel, { color: currentTheme.text }]}>Last Name</Text>
            <TextInput
              value={lastName}
              onChangeText={setLastName}
              style={[styles.textInput, {
                backgroundColor: currentTheme.searchBackground,
                color: currentTheme.text,
              }]}
            />
          </View>

          {/* Email — marked editable={false} since it's read-only */}
          <View style={styles.inputWrapper}>
            <Text style={[styles.inputLabel, { color: currentTheme.text }]}>E-mail</Text>
            <TextInput
              value={user.email}
              editable={false}
              style={[styles.textInput, {
                backgroundColor: currentTheme.searchBackground,
                color: currentTheme.text,
              }]}
            />
          </View>

          {/* Phone Number */}
          <View style={styles.inputWrapper}>
            <Text style={[styles.inputLabel, { color: currentTheme.text }]}>Phone Number</Text>
            <PhoneInput
              defaultValue={phoneValue}
              defaultCode="DM"
              layout="first"
              onChangeText={(text) => setPhoneValue(text)} // FIX: now updates unified phoneValue state
              onChangeFormattedText={(text) => setFormattedValue(text)}
              withDarkTheme
              withShadow
              textInputStyle={{ fontFamily: "Poppins-Medium" }}
              codeTextStyle={{ fontFamily: "Poppins-Medium" }}
              containerStyle={[styles.phoneContainer, {
                backgroundColor: currentTheme.searchBackground,
              }]}
              countryPickerButtonStyle={{ fontFamily: "Poppins-SemiBold" }}
            />
          </View>

        </View>
      </ScrollView>

      {/* Save Button */}
      <TouchableOpacity style={styles.saveButton} onPress={handleSaveChanges}>
        <Text style={styles.saveButtonText}>Save Changes</Text>
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
  headerTitle: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 20,
    flex: 1,
    textAlign: "center",
  },
  profilePictureWrapper: {
    width: "100%",
    height: 170,
    justifyContent: "center",
    alignItems: "center",
  },
  profilePicture: {
    backgroundColor: "grey",
    borderRadius: 60,
    height: 120,
    width: 120,
  },
  changePicButton: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 10,
    marginTop: 10,
    marginBottom: 20,
  },
  formWrapper: {
    flexDirection: "column",
    gap: 10,
    width: "100%",
  },
  inputWrapper: {
    marginBottom: 5,
  },
  inputLabel: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 16,
    marginBottom: 4,
  },
  textInput: {
    height: 50,
    paddingHorizontal: 10,
    borderRadius: 10,
    marginBottom: 2,
    fontFamily: "Poppins-Medium",
  },
  phoneContainer: {
    paddingHorizontal: 10,
    borderRadius: 10,
    marginBottom: 2,
    width: "100%",
  },
  saveButton: {
    borderRadius: 30,
    backgroundColor: "#D4AF37",
    width: "100%",
    justifyContent: "center",
    alignItems: "center",
    padding: 12,
    marginBottom: 40,
  },
  saveButtonText: {
    fontFamily: "Poppins-Medium",
    color: "white",
    fontSize: 15,
  },
});