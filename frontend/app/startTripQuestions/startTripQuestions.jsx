import { StyleSheet, Text, View, TouchableOpacity, Image } from "react-native";
import React, { useState, useContext, useEffect } from "react";
import * as Progress from "react-native-progress";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import CalendarPicker from "react-native-calendar-picker";
import preferences from "../../constants/preferences";
import PreferenceItem from "../../components/PreferenceItem";
import PartyItem from "../../components/partyItem";
import partyOptions from "../../constants/partyOptions";
import budgetOptions from "../../constants/budgetOptions";
import BudgetItem from "../../components/budgetItem";
import { useUserTravelPreferences } from "../contexts/userTravelPreferencesContext";


const StartTripQuestions = () => {
  const [progressBar, setProgressBar] = useState(0.25);
  const [preferenceCount, setPreferenceCount] = useState(0);
  const [selectedPreferences, setSelectedPreferences] = useState([]);
  const [selectedPartyOption, setSelectedPartyOption] = useState(null);
  const [selectedBudgetOption, setSelectedBudgetOption] = useState(null);
  const { theme } = useContext(ThemeContext);
  const [date, setDate] = useState(null);
  const { userTravelPreferences, addPartyId, addStartTripDate, addEndTripDate, addInterests, addBudgetId } = useUserTravelPreferences();

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const minDate = new Date(); // Today
  const maxDate = new Date(2030, 11, 31);

  // To step back the progress bar by 0.25 by pressing the back button.
  const handleBackButton = (progress) => {
    setProgressBar((prev) => prev - 0.25);

  }

  const handleDateChange = (date, type) => {
    if (type === "END_DATE") {
      setDate((prevDate) => {
        return {
          ...prevDate,
          selectedEndDate: date
        };
      })


      addEndTripDate(date);


    }
    else {
      setDate((prevDate) => {
        return {
          ...prevDate,
          selectedStartDate: date
        };
      })

      addStartTripDate(date);
    }

  }

  // console.log(date);

  const togglePreference = (id) => {
    console.log("👉 togglePreference called with id:", id);

    setSelectedPreferences((prev) => {
      console.log("   Current prev state:", prev);

      if (prev.includes(id)) {
        console.log("   ✅ Preference exists. Removing:", id);

        setPreferenceCount((prevCount) => {
          console.log("   Decrementing count:", prevCount, "->", prevCount - 1);
          return prevCount - 1;
        });

        const updated = prev.filter((p) => p !== id);
        console.log("   Updated preferences after removal:", updated);

        addInterests(updated);
        return updated;
      } else {
        if (preferenceCount >= 5) {
          console.log("   ⚠️ Limit reached (5). Cannot add:", id);
          addInterests(prev);
          return prev;
        }

        setPreferenceCount((prevCount) => {
          console.log("   Incrementing count:", prevCount, "->", prevCount + 1);
          return prevCount + 1;
        });

        const updated = [...prev, id]; // 👀 you are adding id+1, not id
        console.log("   ✅ Adding new preference:", id, "=>", id + 1);
        console.log("   Updated preferences after addition:", updated);

        addInterests(updated);
        return updated;
      }
    });
  };

  const togglePartyOption = (id) => {
    setSelectedPartyOption((prevOption) => {
      addPartyId(id);
      return prevOption === id ? null : id;


    });

    console.log("ID: " + id);
  };

  const toggleBudgetOption = (id) => {
    setSelectedBudgetOption((prevOption) => {
      addBudgetId(id);
      return prevOption === id ? null : id;
    });

    console.log("ID: " + id);
  };

  const handleContinueButton = () => {
    // Handle Party Options Validation
    if (progressBar === 0.25) {
      if (!selectedPartyOption) {
        console.log("You must select an option!");
        return;
      }
      else {
        setProgressBar((prev) => prev + 0.25);
      }
    }
    // Handle Trip Date Validation
    else if (progressBar === 0.5) {
      if (!date) {
        console.log("You must pick both start and end dates!")
        return;
      }
      if (date.selectedEndDate === undefined || date.selectedEndDate === null) {
        console.log("Where is the end date broo!!!!!");
        return;
      }
      console.log(date.selectedEndDate)
      setProgressBar((prev) => prev + 0.25);

    }
    // Handle Interets Options
    else if (progressBar === 0.75) {
      if (selectedPreferences.length === 0) {
        console.log("You must select an option!");
        return;
      }
      else {
        setProgressBar((prev) => prev + 0.25);
      }
    }
    else if (progressBar === 1) {
      if (!selectedBudgetOption) {
        console.log("You must select an option!");
        return;
      }
      else {
        router.push('startTripQuestions/reviewSummary')
      }
    }

    // console.log(userTravelPreferences);
    // console.log(date);

  }

  // Everytime the progress bar is changed,check if reached to 0 that way we go to the previous screen,
  useEffect(() => {
    if (progressBar === 0) {
      router.back();
    }

    if (progressBar === 1.25) {
      router.push("startTripQuestions/reviewSummary");
    }
  }, [progressBar])


  const getStepContent = (progressBar) => {
    if (progressBar === 0.25)
      return {
        title: "Who is going? 🧳",
        description:
          "Let's start with the basics. Who's joining you on this adventure?",
        content: partyOptions.map((option, index) => {
          return (
            <PartyItem key={index} title={option.title} description={option.description} onPress={() => { togglePartyOption(index + 1) }} isSelected={selectedPartyOption === index + 1 ? true : false} />
          )
        })
      };
    if (progressBar === 0.5)
      return {
        title: "When will your adventure begin and end? 📅",
        description:
          "Choose the dates for your trip. This helps us plan the perfect itinerary for your travel period.",
        content: (
          <CalendarPicker
            textStyle={{ color: currentTheme.text, fontFamily: "Poppins-Medium" }}
            todayBackgroundColor={currentTheme.searchBackground}
            todayTextStyle={{ color: currentTheme.text }}
            minDate={minDate}
            maxDate={maxDate}
            onDateChange={handleDateChange}
            selectedDayStyle={{ backgroundColor: "#6fc276", padding: 20 }}
            allowRangeSelection={true}
            monthTitleStyle={{ fontFamily: "Poppins-SemiBold" }}
            yearTitleStyle={{ fontFamily: "Poppins-SemiBold" }}
            selectedRangeStartStyle={{ backgroundColor: "#5bcc65ff", }}
            selectedRangeEndStyle={{ backgroundColor: "#5bcc65ff", }}
            selectedRangeStyle={{ backgroundColor: "#5bcc65ff", }}
            selectedRangeStartTextStyle={{ color: "white" }}
            selectedRangeEndTextStyle={{ color: "white" }}
            selectedRangeTextStyle={{ color: "white" }}


            customDayHeaderStyles={() => ({
              textStyle: {
                fontFamily: 'Poppins-SemiBold',
                fontSize: 12,
                letterSpacing: 0.3,
                textTransform: 'uppercase',
              },
            })}

          />
        )
      };
    if (progressBar === 0.75)
      return {
        title: "Tailor your trip to your tastes ✨",
        description: "Select your interests and preferences to make your trip truly yours.",
        content: (
          <View style={styles.preferencesContainer}>
            {preferences.map((item, index) => {
              return (
                <PreferenceItem key={index} title={item.title} isSelected={selectedPreferences.includes(index)}
                  onPress={() => togglePreference(index)} />
              );
            })}
          </View>
        )
      };
    if (progressBar === 1)
      return {
        title: "Set your trip budget 💰",
        description: "Let us know your budget preference and we'll craft an itinerary that suits your financial confort.",
        content: budgetOptions.map((option, index) => {
          return (
            <BudgetItem key={index} title={option.title} description={option.description} onPress={() => { toggleBudgetOption(index + 1) }} isSelected={selectedBudgetOption === index + 1 ? true : false} />
          )
        })
      };
    return "";
  };
  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <View style={styles.backAndProgressBarWrapper}>
        {/* Back Button */}
        <TouchableOpacity onPress={() => handleBackButton(progressBar)}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 30, height: 30, tintColor: currentTheme.iconColor }}
          />
        </TouchableOpacity>
        {/* Progress Bar */}

        <Progress.Bar
          progress={progressBar}
          width={220}
          style={styles.progressBar}
          color="rgba(38, 170, 82, 1)"
          borderColor={currentTheme.searchBackground}
          height={17}
          borderRadius={30}
          unfilledColor={currentTheme.searchBackground}
        />
      </View>

      <Text
        style={{
          fontFamily: "Poppins-SemiBold",
          fontSize: 30,
          marginBottom: 10,
          color: currentTheme.text,
        }}
      >
        {getStepContent(progressBar).title}
      </Text>
      <Text
        style={{
          fontFamily: "Poppins-Regular",
          fontSize: 16,
          marginBottom: 20,
          color: currentTheme.description,
        }}
      >
        {getStepContent(progressBar).description}
      </Text>
      {getStepContent(progressBar).content}

      <TouchableOpacity
        style={{
          borderRadius: 20,
          backgroundColor: "#D4AF37",
          justifyContent: "center",
          alignItems: "center",
          position: "absolute",
          bottom: 30,
          left: 20,
          right: 20,
          padding: 14,
          margin: "auto",
        }}
        onPress={handleContinueButton}
      >
        <Text
          style={{ fontFamily: "Poppins-Medium", color: "white", fontSize: 17 }}
        >
          Continue
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default StartTripQuestions;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: "column",
    paddingTop: 70,
    paddingHorizontal: 30,
    position: "relative",
  },
  backAndProgressBarWrapper: {
    flexDirection: "row",
    alignItems: "center",
    width: "100%",
    marginBottom: 55,
  },

  progressBar: {
    marginLeft: 30,
  },
  preferencesContainer: {
    flexDirection: "row",
    gap: 14,
    marginTop: 10,
    height: "auto",
    flexWrap: "wrap",
  },
});
