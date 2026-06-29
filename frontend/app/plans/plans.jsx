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
import { useUser } from "../contexts/userContext";
import api from "../../src/services/api";
import Constants from "expo-constants";

const { API_BASE_URL } = Constants.expoConfig.extra;

const Plans = () => {
  const { theme } = useContext(ThemeContext);
  const { user } = useUser();

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const plansResponse = await api.get(
        `${API_BASE_URL}/api/subscriptions/plans/`
      );

      setPlans(plansResponse.data);

      if (user?.token) {
        try {
          const subscriptionResponse = await axios.get(
            `${API_BASE_URL}/api/subscriptions/my-subscription/`,
            {
              headers: {
                Authorization: `Bearer ${user.access}`,
              },
            }
          );

          setCurrentSubscription(subscriptionResponse.data);
        } catch {
          setCurrentSubscription(null);
        }
      }
    } catch (err) {
      console.error(err.response?.data || err.message);
    }
  };

  const handleSubscribe = async (planId) => {
    try {
      const response = await api.post(
        `${API_BASE_URL}/api/subscriptions/subscribe/`,
        {
          plan_id: planId,
        },
        {
          headers: {
            Authorization: `Bearer ${user.access}`,
          },
        }
      );

      console.log(response.data);

      router.push({
        pathname: "paymentProcess/selectPayment",
      });
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Failed to subscribe.");
    }
  };

  const handleCancelSubscription = async () => {
    try {
      await axios.post(
        `${API_BASE_URL}/api/subscriptions/unsubscribe/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${user.access}`,
          },
        }
      );

      alert("Subscription cancelled.");
      setCurrentSubscription(null);
      router.replace("/main/settings/");

      loadData();
    } catch (err) {
      console.error(err.response?.data || err.message);
      alert("Failed to cancel subscription.");
    }
  };

  const hasActiveSubscription =
    currentSubscription?.status === "active";

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: currentTheme.background },
      ]}
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
          gap: 25,
          width: 320,
        }}
      >
        {plans.map((item) => {
          const isCurrentPlan =
            hasActiveSubscription &&
            currentSubscription?.plan?.id === item.id;

          return (
            <View
              key={item.id}
              style={[
                styles.subscriptionWrapper,
                {
                  backgroundColor: currentTheme.searchBackground,
                },
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
                  {Number(item.price) === 0
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

              <View style={{ padding: 25 }}>
                {!hasActiveSubscription ? (
                  <TouchableOpacity
                    onPress={() => handleSubscribe(item.id)}
                    style={styles.selectButton}
                  >
                    <Text style={styles.buttonText}>
                      Select Plan
                    </Text>
                  </TouchableOpacity>
                ) : isCurrentPlan ? (
                  <TouchableOpacity
                    onPress={handleCancelSubscription}
                    style={styles.cancelButton}
                  >
                    <Text style={styles.buttonText}>
                      Cancel Subscription
                    </Text>
                  </TouchableOpacity>
                ) : null}
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
    alignItems: "center",
  },

  logoAndSettingsTitle: {
    flexDirection: "row",
    width: "100%",
    marginBottom: 15,
  },

  subscriptionWrapper: {
    width: "100%",
    borderRadius: 10,
    borderWidth: 0.1,
  },

  selectButton: {
    width: "100%",
    backgroundColor: "#D4AF37",
    paddingVertical: 12,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
  },

  cancelButton: {
    width: "100%",
    backgroundColor: "#dc3545",
    paddingVertical: 12,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
  },

  buttonText: {
    color: "#fff",
    fontFamily: "Poppins-Medium",
  },
});