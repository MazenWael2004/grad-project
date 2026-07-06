import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";

const { API_BASE_URL } = Constants.expoConfig.extra;

const api = axios.create({
  baseURL: API_BASE_URL,
});


api.interceptors.request.use(
  async (config) => {
    const access = await AsyncStorage.getItem("access");

    if (access) {
      config.headers.Authorization = `Bearer ${access}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);


api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const refresh = await AsyncStorage.getItem("refresh");

        const response = await axios.post(
          `${API_BASE_URL}/api/accounts/token/refresh/`,
          {
            "refresh":refresh,
          }
        );

        const newAccess = response.data.access;

        await AsyncStorage.setItem(
          "access",
          newAccess
        );

        originalRequest.headers.Authorization =
          `Bearer ${newAccess}`;

        return api(originalRequest);
      } catch (refreshError) {
        await AsyncStorage.multiRemove([
          "access",
          "refresh",
          "user",
        ]);

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;