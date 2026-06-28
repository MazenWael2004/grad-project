import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { useContext, useEffect, useState } from "react";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import subscriptions from "../../constants/subscriptions";
import { useUser } from "../contexts/userContext";
import axios from "axios";
import Constants from "expo-constants";
const { API_BASE_URL } = Constants.expoConfig.extra;
// import {useUser} from '../contexts/userContext'

const Plans = () => {
  const [plans, setPlans] = useState([]);
  const handleSubscribe = async (planId) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/subscriptions/subscribe/`,
        {
          plan_id: planId,
        },
        {
          headers: {
            Authorization: `Token ${user.token}`, // if your API requires JWT
          },
        },
      );

      console.log(response.data);

      // Update local user state if you have setUser
      // setUser(prev => ({
      //   ...prev,
      //   subscriptionID: response.data.subscription_id,
      // }));

      alert(`Subscribed to ${response.data.plan}!`);
      router.push({
        pathname: "paymentProcess/selectPayment",
      })
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Failed to subscribe.");
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/api/subscriptions/plans/`,
        );
        setPlans(response.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, []);

  const { theme } = useContext(ThemeContext);
  const { user } = useUser();
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
        {plans.map((item, indx) => {
          const isCurrentPlan = user?.subscriptionID === item.id;
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
                  {item.price === 0
                    ? "Free"
                    : `${Math.floor(Number(item.price))}/month`}
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
                {/* {item.features.map((feature, indx2) => {
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
                })} */}

                <View
                  style={{
                    borderBottomColor: currentTheme.borderBottomColor,
                    borderBottomWidth: 1,
                    width: "100%",
                    height: 10,
                    marginBottom: 10,
                  }}
                />

                <TouchableOpacity
                  onPress={() => {
                    console.log("Item:", item);
                    handleSubscribe(item.id);
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
