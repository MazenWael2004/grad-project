
import '@livekit/react-native';
import 'react-native-get-random-values';


import {
  registerGlobals,
} from '@livekit/react-native';
registerGlobals();

import { Stack } from "expo-router";
import { ThemeProvider } from "../theme/ThemeContext";
import {UserTravelPreferencesProvider} from "./contexts/userTravelPreferencesContext"

import {ArabicLanguageProvider} from "./contexts/arabicLanguageContext"
import {ItineraryProvider} from "./contexts/itineraryContext"
import {SavedListProvider} from "./contexts/savedListContext"
import { RegisterFormProvider} from './contexts/registerFormContext'
import {UserProvider} from './contexts/userContext';
 


export default function RootLayout() {

  return (
    <UserProvider>
    <RegisterFormProvider>
    <SavedListProvider>
    <ItineraryProvider>
    <ArabicLanguageProvider>
   <UserTravelPreferencesProvider>
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
        name="governorateDetails/[governorateId]"
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

      <Stack.Screen
      name="startTripQuestions/reviewSummary"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="chatbot/index"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="generatingTripLoading/index"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="itineraryDetails/[itineraryId]"
      options={{headerShown:false}}

      />

      <Stack.Screen
      name="countryPicker/index"
      options={{headerShown:false}}
      />

      <Stack.Screen
      name="articleDetails/[articleId]"
      options={{headerShown:false}}
      />

      <Stack.Screen
      name="settings/billingSubscriptions"
      options={{headerShown:false}}
      />

       <Stack.Screen
      name="paymentProcess/selectPayment"
      options={{headerShown:false}}
      />

       <Stack.Screen
      name="paymentProcess/reviewSummary"
      options={{headerShown:false}}
      />

        <Stack.Screen
      name="successMessage/paymentCompleted"
      options={{headerShown:false}}
      />

      <Stack.Screen
      name="currencyConverter/index"
      options={{headerShown:false}}
      />

      <Stack.Screen
      name = "tourGuide"
      options={{headerShown:false}}
      />
     
    </Stack>
  
     </ThemeProvider>
     </UserTravelPreferencesProvider>
     </ArabicLanguageProvider>
     </ItineraryProvider>
     </SavedListProvider>
     </RegisterFormProvider>
     </UserProvider>
  );
}
    

