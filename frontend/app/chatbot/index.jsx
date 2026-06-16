import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { useState, useContext, useRef, useEffect } from "react";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import messages from "../../constants/messages";
import { Ionicons } from "@expo/vector-icons";
import { useCameraPermissions } from "expo-camera";

import { useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback } from "react";


const ChatBot = () => {
  const params = useLocalSearchParams();
  const { theme } = useContext(ThemeContext);

  const [prompt, setPrompt] = useState("");
  const [messagesList, setMessagesList] = useState(messages);
  const [isPromptSubmitted, setIsPromptSubmitted] = useState(false);
  const [isPromptEmpty, setIsPromptEmpty] = useState(true);
  const [loading, setLoading] = useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const [predictionAdded, setPredictionAdded] = useState(false);

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const scrollViewRef = useRef(null);

  const API_URL = "https://7570-34-21-71-3.ngrok-free.app/generate";
  const API_KEY = "secret123";

  

useEffect(() => {
  if (!params?.label) return;

  setMessagesList((prev) => {
    const alreadyExists = prev.some(
      (msg) =>
        msg.text ===
        `📍 Detected: ${params.label} (${Number(params.confidence).toFixed(1)}%)`
    );

    if (alreadyExists) return prev;

    return [
      ...prev,
      {
        id: prev.length + 1,
        text: `📍 Detected: ${params.label} (${Number(params.confidence).toFixed(1)}%)`,
        role: "bot",
        photo: require("../../assets/images/chatbot.png"),
      },
    ];
  });

  setIsPromptSubmitted(true);
}, [params?.label, params?.confidence]);


  const handleCameraButton = async () => {
    console.log("Camera button pressed");

    if (!permission?.granted) {
      const result = await requestPermission();

      if (!result.granted) {
        console.log("Camera permission denied");
        return;
      }
    }

    
    router.push("/camera");
  };

  const handleSendButton = async () => {
    if (!prompt.trim()) return;

    setIsPromptSubmitted(true);
    setLoading(true);

    setMessagesList((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        text: prompt,
        role: "user",
        photo: require("../../assets/images/avatar.png"),
      },
    ]);

    const userMessage = prompt;
    setPrompt("");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: userMessage,
          max_length: 400,
        }),
      });

      if (res.ok) {
        const data = await res.json();

        setMessagesList((prev) => [
          ...prev,
          {
            id: prev.length + 1,
            text: data.response || "Sorry, I didn’t understand that.",
            role: "bot",
            photo: require("../../assets/images/chatbot.png"),
          },
        ]);
      } else {
        setMessagesList((prev) => [
          ...prev,
          {
            id: prev.length + 1,
            text: "Error connecting to EgyBot API.",
            role: "bot",
            photo: require("../../assets/images/chatbot.png"),
          },
        ]);
      }
    } catch (err) {
      console.log("CHATBOT ERROR:", err);

      setMessagesList((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          text: `Error: ${err.message}`,
          role: "bot",
          photo: require("../../assets/images/chatbot.png"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordButton = () => {
    console.log("Record button pressed");
  };

  useEffect(() => {
    if (scrollViewRef.current) {
      scrollViewRef.current.scrollToEnd({ animated: true });
    }

    setIsPromptEmpty(prompt.trim() === "");
  }, [messagesList, prompt]);

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <View
        style={[styles.container, { backgroundColor: currentTheme.background }]}
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
              fontFamily: "Poppins-Bold",
              fontSize: 20,
              color: currentTheme.text,
              marginLeft: 20,
              flex: 1,
            }}
          >
            EgyBot
          </Text>

        
          <TouchableOpacity onPress={handleCameraButton}>
            <Ionicons
              name="camera-outline"
              size={28}
              color={currentTheme.iconColor}
            />
          </TouchableOpacity>
        </View>

        {/* MESSAGES */}
        {!isPromptSubmitted ? (
          <View style={styles.greetingWrapper}>
            <Image
              source={require("../../assets/images/chatbot.png")}
              style={{ width: 150, height: 150 }}
            />
            <Text style={styles.title}>Hello, User!</Text>
            <Text style={styles.subtitle}>
              Welcome to EgyBot, your AI tour guide.
            </Text>
          </View>
        ) : (
          <ScrollView
            ref={scrollViewRef}
            style={{ flex: 1 }}
            contentContainerStyle={styles.answersWrapper}
          >
            {messagesList.map((msg, index) => (
              <View key={index} style={styles.answer}>
                <View style={styles.whoAnsweredWrapper}>
                  <Image source={msg.photo} style={{ width: 40, height: 40 }} />
                  <Text style={{ color: currentTheme.text }}>
                    {msg.role === "user" ? "You" : "EgyBot"}
                  </Text>
                </View>

                <Text style={{ color: currentTheme.text }}>{msg.text}</Text>
              </View>
            ))}

            {loading && (
              <View style={styles.loaderWrapper}>
                <ActivityIndicator size="large" color="#D4AF37" />
                <Text style={{ color: currentTheme.text }}>
                  EgyBot is typing...
                </Text>
              </View>
            )}
          </ScrollView>
        )}

        {/* INPUT */}
        <View style={styles.promptWrapper}>
          <TextInput
            style={styles.textInput}
            placeholder="Ask me anything..."
            value={prompt}
            onChangeText={setPrompt}
            multiline
          />

          <TouchableOpacity
            onPress={isPromptEmpty ? handleRecordButton : handleSendButton}
            style={styles.sendButton}
          >
            <Image
              source={
                isPromptEmpty
                  ? require("../../assets/images/voice.png")
                  : require("../../assets/images/send.png")
              }
              style={styles.sendIcon}
            />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

export default ChatBot;

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 70, paddingHorizontal: 20 },

  backAndPersonalInfoTitle: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
  },

  greetingWrapper: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  title: { fontSize: 32, fontWeight: "bold" },
  subtitle: { fontSize: 18, textAlign: "center", marginTop: 10 },

  answersWrapper: { paddingBottom: 20 },

  answer: { marginVertical: 10 },

  whoAnsweredWrapper: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },

  loaderWrapper: {
    alignItems: "center",
    marginVertical: 10,
  },

  promptWrapper: {
    flexDirection: "row",
    alignItems: "center",
    padding: 10,
  },

  textInput: {
    flex: 1,
    backgroundColor: "#eee",
    borderRadius: 20,
    padding: 10,
  },

  sendButton: {
    marginLeft: 10,
    backgroundColor: "#D4AF37",
    padding: 12,
    borderRadius: 30,
  },

  sendIcon: {
    width: 20,
    height: 20,
  },
});