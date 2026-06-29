import 'dotenv/config';

export default {
  expo: {
    name: "my-app",
    slug: "my-app",
    version: "1.0.0",
    android: {
      package: "com.basharr.myapp",
      config: {
        googleMaps: {
          apiKey: process.env.GOOGLE_MAPS_API_KEY || "AIzaSyBYwvams1qk168bh-_NkvilKyAuN2nHbVA",
        },
      },
    },
    extra: {
      API_BASE_URL: process.env.API_BASE_URL,
    },
    plugins: [
      "@livekit/react-native-expo-plugin",
      "@config-plugins/react-native-webrtc"
    ]
  },
};
