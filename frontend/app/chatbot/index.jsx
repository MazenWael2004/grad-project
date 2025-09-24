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
} from "react-native";
import { useState, useContext, useRef, useEffect } from "react";
import { router } from "expo-router";
import { ThemeContext } from "../../theme/ThemeContext";
import { LIGHT_THEME, DARK_THEME } from "../../constants/themes";
import messages from "../../constants/messages";

const ChatBot = () => {
  const { theme } = useContext(ThemeContext);
  const [prompt, setPrompt] = useState(""); // Actual prompt input by user
  const [messagesList,setMessagesList] = useState(messages); // List of messages exchanged
  const [isPromptSubmitted, setIsPromptSubmitted] = useState(false); // To track if user has submitted a prompt

  const currentTheme = theme === "Light" ? LIGHT_THEME : DARK_THEME;
  const scrollViewRef = useRef(null);
 
  // Function to handle prompt input change
  const handlePromptChange = (text) => {
    setPrompt(text);
  };
 
  // Function to handle sending the prompt
  const handleSendButton = () =>{
    setIsPromptSubmitted(true);
    setMessagesList((prevMessagesList)=>{
        return [
            ...prevMessagesList,
            {
                id:prevMessagesList.length+1,
                text:prompt,
                role:"user",
                photo:require("../../assets/images/avatar.png"),
            }
        ]
    })
    setPrompt(""); // Clear input field after sending
  }

  // Auto-scroll to bottom when new message is sent
  useEffect(() => {
    if (scrollViewRef.current) {
      scrollViewRef.current.scrollToEnd({ animated: true });
    }
  }, [isPromptSubmitted]);

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View
        style={[styles.container, { backgroundColor: currentTheme.background }]}
      >
        {/* Header */}
        <View style={styles.backAndPersonalInfoTitle}>
          <TouchableOpacity onPress={() => router.back()}>
            <Image
              source={require("../../assets/images/back.png")}
              style={{ width: 30, height: 30, tintColor: currentTheme.iconColor }}
            />
          </TouchableOpacity>
          <Text
            style={{
              fontFamily: "Poppins-Bold",
              fontSize: 20,
              color: currentTheme.text,
              marginLeft: 20,
            }}
          >
            EgyBot
          </Text>
        </View>

        {/* Greeting or Messages */}
        {!isPromptSubmitted ? (
          <View style={styles.greetingWrapper}>
            <Image
              source={require("../../assets/images/chatbot.png")}
              style={{ width: 150, height: 150 }}
            />
            <Text
              style={{
                fontFamily: "Poppins-SemiBold",
                fontSize: 32,
                color: currentTheme.text,
              }}
            >
              Hello, User!
            </Text>

            <Text
              style={{
                fontFamily: "Poppins-SemiBold",
                fontSize: 28,
                color: currentTheme.text,
                textAlign: "center",
                marginVertical: 10,
              }}
            >
              Welcome to EgyBot, your AI tour guide.
            </Text>

            <Text
              style={{
                fontFamily: "Poppins-Medium",
                fontSize: 16,
                color: currentTheme.description,
                textAlign: "center",
              }}
            >
              Ask anything about our beloved country.
            </Text>
          </View>
        ) : (
          <ScrollView
            ref={scrollViewRef}
            style={{ flex: 1 }}
            contentContainerStyle={styles.answersWrapper}
            showsVerticalScrollIndicator={false}
          >
            {/* User message */}
            
            {messagesList.map((messageItem,index)=>{
                return (
                   <View style={styles.answer} key={index}>
              <View style={styles.whoAnsweredWrapper}>
                <Image
                  source={messageItem.photo}
                  style={{ width: 40, height: 40 }}
                />
                <Text
                  style={{
                    fontFamily: "Poppins-Medium",
                    fontSize: 18,
                    color: currentTheme.text,
                  }}
                >
                  {messageItem.role==="user"?"Mazen Wael":"EgyBot"}
                </Text>
              </View>
              <Text
                style={{
                  fontFamily: "Poppins-Medium",
                  fontSize: 15,
                  color: currentTheme.text,
                  marginTop: 5,
                }}
              >
                {messageItem.text}
              </Text>
            </View> 
                )
            })}
          </ScrollView>
        )}

        {/* Input bar */}
        <View style={[styles.promptWrapper,{backgroundColor:currentTheme.background}]}>
          <TextInput
            style={[
              styles.textInput,
              {
                color: currentTheme.text,
                backgroundColor: currentTheme.searchBackground,
                borderColor: currentTheme.borderColor,
              },
            ]}
            placeholder="Ask me anything about Egypt..."
            placeholderTextColor={currentTheme.description}
            multiline
            onSubmitEditing={() => setIsPromptSubmitted(true)}
            onChangeText={handlePromptChange}
            value={prompt}
          />
          <TouchableOpacity
            onPress={handleSendButton}
            style={styles.sendButton}
          >
            <Image
              source={require("../../assets/images/send.png")}
              style={[styles.sendIcon, { tintColor: currentTheme.background }]}
            />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

export default ChatBot;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 20,
  },
  backAndPersonalInfoTitle: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
  },
  greetingWrapper: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  answersWrapper: {
    paddingBottom: 20,
  },
  answer: {
    flexDirection: "column",
    paddingVertical: 5,
  },
  whoAnsweredWrapper: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  promptWrapper: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 10,
    paddingHorizontal: 10,
    backgroundColor: "white",
    borderTopWidth: 1,
    borderColor: "#ddd",
  },
  textInput: {
    flex: 1,
    fontFamily: "Poppins-Medium",
    fontSize: 16,
    padding: 12,
    borderRadius: 20,
    maxHeight: 120, // keeps input from growing too tall
  },
  sendButton: {
    marginLeft: 10,
    backgroundColor: "#D4AF37",
    padding: 12,
    borderRadius: 30,
    justifyContent: "center",
    alignItems: "center",
  },
  sendIcon: {
    width: 20,
    height: 20,
  },
});
