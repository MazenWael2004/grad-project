import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
  Image,
  ActivityIndicator,
  FlatList,
} from "react-native";
import React, { useContext, useState, useMemo } from "react";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import { router } from "expo-router";
import data from "../../src/data.json";
import { debounce } from "lodash";
import { useRegisterFormContext } from "../contexts/registerFormContext";
// Optional: use FastImage for better performance
// import FastImage from 'react-native-fast-image';

const CountryPicker = () => {
  const { theme } = useContext(ThemeContext);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  const [searchInput, setSearchInput] = useState("");
  const {registerFormData,setRegisterFormData} = useRegisterFormContext();
  const [selectedCountry,setSelectedCountry] = useState("");

  // Debounced search handler
  const handleSearch = useMemo(
    () => debounce((text) => setSearchInput(text), 300),
    []
  );

  // Memoized filtered countries
  const filteredCountries = useMemo(() => {
    return data.filter((item) =>
      item.name.toLowerCase().includes(searchInput.toLowerCase())
    );
  }, [searchInput]);

  return (
    <View style={[styles.container, { backgroundColor: currentTheme.background }]}>
      {/* Header */}
      <View style={styles.backAndPersonalInfoTitle}>
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 30, height: 30, tintColor: currentTheme.iconColor }}
          />
        </TouchableOpacity>
        <Text style={[styles.title, { color: currentTheme.text }]}>
          Select Country
        </Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchBarWrapper}>
        <TextInput
          style={[
            styles.searchBar,
            {
              backgroundColor: currentTheme.searchBackground,
              color: currentTheme.text,
            },
          ]}
          placeholder="Search Your Country..."
          placeholderTextColor="#888"
          textAlignVertical="center"
          onChangeText={handleSearch}
        />
        <Image
          source={require("../../assets/images/magnifying-glass.png")}
          style={styles.searchIcon}
        />
      </View>

      {/* Country List */}
      {filteredCountries.length === 0 ? (
        <ActivityIndicator size="large" color="#007AFF" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={filteredCountries}
          keyExtractor={(item) => item.name}
          initialNumToRender={10}
          windowSize={5}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 50 }}
          renderItem={({ item }) => (
            <TouchableOpacity style={styles.countryItem} onPress={()=>{
              setRegisterFormData((prev)=>{
                return {
                  ...prev,
                  country:item.name,
                }
              })
router.push({
  pathname: "authentication/register",
  params: { country: item.name },
})

            }
}>
              <View style={{ flexDirection: "row", gap: 15, alignItems: "center" }}>
                {/* Use FastImage for better performance if needed */}
                {/* <FastImage
                  source={{ uri: item.flags.png }}
                  style={{ width: 80, height: 60 }}
                  resizeMode={FastImage.resizeMode.contain}
                /> */}
                <Image
                  source={{ uri: item.flags.png }}
                  style={{ width: 80, height: 60 }}
                />
                <Text style={{ fontFamily: "Poppins-Medium", color: currentTheme.text }}>
                  {item.name}
                </Text>
              </View>
              <Image
                source={require("../../assets/images/check.png")}
                style={{ width: 25, height: 25 }}
              />
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
};

export default CountryPicker;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
  },
  backAndPersonalInfoTitle: {
    flexDirection: "row",
    alignItems: "center",
    width: "90%",
    marginBottom: 15,
  },
  title: {
    fontFamily: "Poppins-SemiBold",
    fontSize: 20,
    marginLeft: "auto",
    marginRight: "auto",
  },
  searchBarWrapper: {
    marginTop: 20,
    position: "relative",
    flexDirection: "row",
    alignItems: "center",
  },
  searchBar: {
    flex: 1,
    height: 65,
    borderRadius: 15,
    paddingLeft: 20,
    paddingRight: 50,
    fontFamily: "Poppins-Regular",
    fontSize: 14,
    marginBottom: 20,
  },
  searchIcon: {
    position: "absolute",
    right: 22,
    top: 20,
    width: 24,
    height: 24,
    tintColor: "#888",
  },
  countryItem: {
    padding: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderColor: "#888",
    borderWidth: 0.2,
    borderRadius: 10,
    marginBottom:20,
  },
});

