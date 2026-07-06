import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";
import { useCallback, useContext, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import api from "../../src/services/api";

import { DARK_THEME, LIGHT_THEME } from "../../constants/themes";
import { ThemeContext } from "../../theme/ThemeContext";
import { useUser } from "../contexts/userContext";

const Billing = () => {
  const { theme } = useContext(ThemeContext);
  const { user } = useUser();

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;

  const [plan, setPlan] = useState(null);
  const [planStatus, setPlanStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadCurrentPlan = useCallback(async () => {
    try {
      setLoading(true);

      const access = user?.access || (await AsyncStorage.getItem("access"));

      if (!access) {
        setPlan(null);
        setPlanStatus(null);
        return;
      }

      const response = await api.get("/api/subscriptions/my-subscription/");

      setPlan(response.data.plan);
      setPlanStatus(response.data.status ?? null);
    } catch (error) {
      console.error(
        "Failed to load subscription:",
        error.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  }, [user?.access]);

  useEffect(() => {
    loadCurrentPlan();
  }, [loadCurrentPlan]);
  const handleCancelPending = async () => {
    try {
      await api.post(
        "/api/subscriptions/cancel-pending-subscription/"
      );

      await loadCurrentPlan();
    } catch (error) {
      console.error(
        "Failed to cancel pending subscription:",
        error.response?.data || error.message
      );
    }
  };

  const handlePay = () => {
    router.push("paymentProcess/selectPayment");
  };
  if (loading) {
    return (
      <View
        style={[
          styles.container,
          {
            backgroundColor: currentTheme.background,
            justifyContent: "center",
            alignItems: "center",
          },
        ]}
      >
        <ActivityIndicator size="large" color="#D4AF37" />
        <Text
          style={{
            marginTop: 15,
            color: currentTheme.text,
            fontFamily: "Poppins-Medium",
          }}
        >
          Loading subscription...
        </Text>
      </View>
    );
  }

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: currentTheme.background },
      ]}
    >
      <View style={styles.backAndPersonalInfoTitle}>
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{
              width: 30,
              height: 30,
              tintColor: currentTheme.iconColor,
            }}
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
          Billing & Plans
        </Text>
      </View>

      <View
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
              fontSize: 22,
            }}
          >
            {plan?.name ?? "No Active Plan"}
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
              color: currentTheme.text,
            }}
          >
            {plan
              ? plan.price === 0
                ? "Free"
                : `${plan.price} L.E/month`
              : "--"}
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-Medium",
              color:
                planStatus === "active"
                  ? "#28a745"
                  : "#e24646",
              marginBottom: 15,
            }}
          >
            Status: {planStatus ?? "Unknown"}
          </Text>
        </View>

        <View
          style={{
            borderBottomColor: currentTheme.borderBottomColor,
            borderBottomWidth: 1,
            width: "100%",
            marginBottom: 20,
          }}
        />
        {planStatus === "pending" && (
          <View
            style={{
              width: "100%",
              paddingHorizontal: 25,
              marginBottom: 20,
              gap: 12,
            }}
          >
            <TouchableOpacity
              onPress={handlePay}
              style={{
                backgroundColor: "#D4AF37",
                paddingVertical: 14,
                borderRadius: 8,
                alignItems: "center",
              }}
            >
              <Text
                style={{
                  color: "white",
                  fontFamily: "Poppins-SemiBold",
                }}
              >
                Continue Payment
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleCancelPending}
              style={{
                backgroundColor: "#e24646",
                paddingVertical: 14,
                borderRadius: 8,
                alignItems: "center",
              }}
            >
              <Text
                style={{
                  color: "white",
                  fontFamily: "Poppins-SemiBold",
                }}
              >
                Cancel Subscription
              </Text>
            </TouchableOpacity>
          </View>
        )}
        <View
          style={{
            paddingHorizontal: 25,
            paddingBottom: 25,
          }}
        >
          <Text
            style={{
              textAlign: "center",
              fontFamily: "Poppins-Medium",
              color: "#9b9b9b",
            }}
          >
            Your current subscription plan
          </Text>
        </View>
      </View>
    </View>
  );
};

export default Billing;

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
    marginBottom: 35,
  },

  subscriptionWrapper: {
    width: "100%",
    borderRadius: 10,
    borderWidth: 0.5,
    overflow: "hidden",
  },
});
