import { Stack } from "expo-router";
import { DarkTheme, DefaultTheme } from "@react-navigation/native";
import { Slot } from "expo-router";
import { ThemeProvider } from "../theme/ThemeContext";



export default function RootLayout() {

  return (
   
    <ThemeProvider>
     <Stack>
      <Stack.Screen
        name="index"
        options={{headerShown: false}}
       />
      <Stack.Screen
        name="onboarding/index"
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="authentication/login"
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="authentication/register"
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="personalization/travelPreferences"
        options={{headerShown: false}}
      />
       <Stack.Screen
        name="successMessage/signUpCompleted"
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="main/index"
        options={{headerShown: false}}
      />

      <Stack.Screen
        name="main"
        options={{headerShown: false}}
      />
      
      <Stack.Screen
        name="tripDetails/[tripId]"
        options={{headerShown:false}}
      
      />

      <Stack.Screen
      name="viewAll/popularPlaces"
      options={{headerShown:false}}

      />

        <Stack.Screen
      name="plans/plans"
      options={{headerShown:false}}

      />

       <Stack.Screen
      name="settings/personalInfo"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="settings/paymentMethods"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="viewAll/popularArticles"
      options={{headerShown:false}}
      />

      <Stack.Screen
      name="settings/emergencySupport"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="addPaymentMethod/index"
      options={{headerShown:false}}
      
      />
      <Stack.Screen
      name="startTripQuestions/startTripQuestions"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="appAppearance/index"
      options={{headerShown:false}}

      />

     
    </Stack>
  
     </ThemeProvider>
  );
}
    

