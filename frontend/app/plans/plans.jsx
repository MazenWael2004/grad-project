import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { useContext } from "react";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import subscriptions from "../../constants/subscriptions";
import { useUser } from "../contexts/userContext";
// import {useUser} from '../contexts/userContext'

const Plans = () => {
  const { theme } = useContext(ThemeContext);
  const {user} = useUser();
  // console.log(user);
  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  return (
    <View
      style={[styles.container, { backgroundColor: currentTheme.background }]}
    >
      <View style={styles.logoAndSettingsTitle}>
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{
              width: 35,
              height: 35,
              resizeMode: "contain",
              tintColor: currentTheme.iconColor,
            }}
          />
        </TouchableOpacity>
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: currentTheme.text,
            marginLeft: 60,
          }}
        >
          Upgrade Plan
        </Text>
      </View>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          flexDirection: "column",
          gap: 25,
          justifyContent: "center",
          width: 320,
        }}
      >
        {subscriptions.map((item, indx) => {
           const isCurrentPlan = user?.currentSubscription?.id === item.id;
          return (
            <View
              key={indx}
              style={[
                styles.subscriptionWrapper,
                { backgroundColor: currentTheme.searchBackground },
              ]}
            >
              <View
                style={{
                  width: "100%",
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    fontFamily: "Poppins-SemiBold",
                    marginBottom: 10,
                    marginTop: 19,
                    color: currentTheme.text,
                  }}
                >
                  {item.name}
                </Text>

                <Text
                  style={{
                    fontFamily: "Poppins-SemiBold",
                    marginBottom: 10,
                    fontSize: 35,
                    color: currentTheme.text,
                  }}
                >
                  {item.price === 0 ? "Free" : `${Math.floor(item.price * user.exchangeRate)}/month`}
                </Text>
              </View>

              <View
                style={{
                  borderBottomColor: currentTheme.borderBottomColor,
                  borderBottomWidth: 1,
                  width: "100%",
                  height: 10,
                }}
              />

              <View style={{ flexDirection: "column", gap: 10, padding: 25 }}>
                {item.features.map((feature, indx2) => {
                  return (
                    <View
                      key={indx2}
                      style={{
                        flexDirection: "row",
                        alignItems: "center",
                        gap: 10,
                      }}
                    >
                      <Image
                        source={require("../../assets/images/check.png")}
                        style={{
                          width: 15,
                          height: 15,
                          tintColor: currentTheme.iconColor,
                        }}
                      />

                      <Text
                        style={{
                          fontFamily: "Poppins-Medium",
                          fontSize: 13,
                          color: currentTheme.text,
                        }}
                      >
                        {feature}
                      </Text>
                    </View>
                  );
                })}

                <View
                  style={{
                    borderBottomColor: currentTheme.borderBottomColor,
                    borderBottomWidth: 1,
                    width: "100%",
                    height: 10,
                    marginBottom: 10,
                  }}
                />
                {isCurrentPlan ? (
                  <Text
                    style={{
                      textAlign: "center",
                      fontFamily: "Poppins-Medium",
                      color: "#b7b7b7ff",
                    }}
                  >
                    Your current plan
                  </Text>
                ) : (
                  <TouchableOpacity
                    onPress={() => {
                      router.push({
                        pathname: "paymentProcess/selectPayment",
                        params: { subscription:JSON.stringify(item)  },
                      });
                    }}
                    style={{
                      width: "100%",
                      backgroundColor: "#D4AF37",
                      paddingHorizontal: 15,
                      paddingVertical: 10,
                      justifyContent: "center",
                      alignItems: "center",
                      borderRadius: 20,
                    }}
                  >
                    <Text
                      style={{ fontFamily: "Poppins-Medium", color: "white" }}
                    >
                      Select Plan
                    </Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
};

export default Plans;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "column",
    alignItems: "center",
  },
  logoAndSettingsTitle: {
    flexDirection: "row",
    width: "100%",
    marginBottom: 15,
  },
  subscriptionWrapper: {
    position: "relative",
    width: "100%",
    height: "auto",
    backgroundColor: "#e7e7e7ff",
    borderRadius: 10,
    borderWidth: 0.1,
  },
});
