import React, { useRef, useState, useEffect } from "react";
import {
  View,
  TouchableOpacity,
  Text,
  ActivityIndicator,
  Image,
  Animated,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";

export default function CameraScreen() {
  const cameraRef = useRef(null);

  const [permission, requestPermission] = useCameraPermissions();

  const [loading, setLoading] = useState(false);
  const [classifier, setClassifier] = useState("custom");

  const [photoUri, setPhotoUri] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const CUSTOM_MODEL_URL =
    "http://192.168.1.221:8001/api/classify-image/";

  const GEMINI_URL =
    "https://12e1-8-229-115-241.ngrok-free.app/gemini-predict";

  // const API_KEY = "secret123";


  const flashAnim = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const imageOpacity = useRef(new Animated.Value(0)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;
  const scanAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!permission?.granted) {
      requestPermission();
    }
  }, [permission]);


  useEffect(() => {
    if (loading) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(scanAnim, {
            toValue: 400,
            duration: 1200,
            useNativeDriver: true,
          }),
          Animated.timing(scanAnim, {
            toValue: 0,
            duration: 1200,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [loading]);

  if (!permission?.granted) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ marginBottom: 10 }}>
          Camera permission required
        </Text>

        <TouchableOpacity
          onPress={requestPermission}
          style={{
            padding: 12,
            backgroundColor: "#D4AF37",
            borderRadius: 8,
          }}
        >
          <Text style={{ color: "white" }}>Allow Camera</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const animateButton = () => {
    Animated.sequence([
      Animated.timing(buttonScale, {
        toValue: 0.9,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(buttonScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const flash = () => {
    Animated.sequence([
      Animated.timing(flashAnim, {
        toValue: 1,
        duration: 80,
        useNativeDriver: true,
      }),
      Animated.timing(flashAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const takePicture = async () => {
    if (!cameraRef.current || loading) return;

    try {
      animateButton();
      flash();

      setLoading(true);
      setPrediction(null);

      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.7,
      });

      setPhotoUri(photo.uri);

      Animated.timing(imageOpacity, {
        toValue: 1,
        duration: 500,
        useNativeDriver: true,
      }).start();

      const formData = new FormData();
      formData.append("file", {
        uri: photo.uri,
        type: "image/jpeg",
        name: "photo.jpg",
      });

      const API_URL =
        classifier === "custom"
          ? CUSTOM_MODEL_URL
          : GEMINI_URL;

      const res = await fetch(CUSTOM_MODEL_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access}`,
        },
        body: formData,
      });

      // const text = await res.text();

      // console.log("Status:", res.status);
      // console.log("Response:", text);

      const data = await res.json();

      console.log("Status:", res.status);
      console.log("MODEL RESULT:", data);

      setPrediction({
        label: data.label,
        confidence: data.confidence,
      });

      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }).start();
    } catch (err) {
      console.log("Camera Error:", err);

      setPrediction({
        label: "Error",
        confidence: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const retakePhoto = () => {
    setPhotoUri(null);
    setPrediction(null);
    fadeAnim.setValue(0);
    imageOpacity.setValue(0);
  };

  return (
    <View style={{ flex: 1 }}>
      {photoUri ? (
        <>
          <Animated.Image
            source={{ uri: photoUri }}
            style={{
              flex: 1,
              opacity: imageOpacity,
            }}
            resizeMode="contain"
          />


          {loading && (
            <Animated.View
              style={{
                position: "absolute",
                left: 30,
                right: 30,
                height: 3,
                backgroundColor: "#00FFAA",
                transform: [{ translateY: scanAnim }],
              }}
            />
          )}


          {loading && (
            <View
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                justifyContent: "center",
                alignItems: "center",
                backgroundColor: "rgba(0,0,0,0.3)",
              }}
            >
              <ActivityIndicator size="large" color="#fff" />
              <Text style={{ color: "white", marginTop: 10 }}>
                Analyzing...
              </Text>
            </View>
          )}

          {prediction && !loading && (
            <Animated.View
              style={{
                opacity: fadeAnim,
                position: "absolute",
                bottom: 120,
                alignSelf: "center",
                backgroundColor: "rgba(255,255,255,0.15)",
                padding: 15,
                borderRadius: 12,
                borderWidth: 1,
                borderColor: "rgba(255,255,255,0.3)",
              }}
            >
              <Text style={{ color: "white", fontSize: 18, fontWeight: "bold" }}>
                {prediction.label}
              </Text>

              <Text style={{ color: "white", marginTop: 5 }}>
                Confidence: {Number(prediction.confidence).toFixed(2)}%
              </Text>
            </Animated.View>
          )}

          <TouchableOpacity
            onPress={retakePhoto}
            style={{
              position: "absolute",
              bottom: 40,
              alignSelf: "center",
              backgroundColor: "#D4AF37",
              paddingHorizontal: 30,
              paddingVertical: 15,
              borderRadius: 30,
            }}
          >
            <Text style={{ color: "white", fontWeight: "bold" }}>
              Retake Photo
            </Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <CameraView ref={cameraRef} style={{ flex: 1 }} />


          <View
            style={{
              position: "absolute",
              top: 60,
              alignSelf: "center",
              flexDirection: "row",
            }}
          >
            <TouchableOpacity
              onPress={() => setClassifier("custom")}
              style={{
                backgroundColor:
                  classifier === "custom" ? "#D4AF37" : "white",
                padding: 10,
                borderRadius: 8,
                marginRight: 10,
              }}
            >
              <Text>Our Model</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => setClassifier("gemini")}
              style={{
                backgroundColor:
                  classifier === "gemini" ? "#D4AF37" : "white",
                padding: 10,
                borderRadius: 8,
              }}
            >
              <Text>Gemini AI</Text>
            </TouchableOpacity>
          </View>

          <Animated.View
            style={{
              transform: [{ scale: buttonScale }],
              position: "absolute",
              bottom: 50,
              alignSelf: "center",
            }}
          >
            <TouchableOpacity
              onPress={takePicture}
              style={{
                backgroundColor: "white",
                padding: 20,
                borderRadius: 50,
                elevation: 5,
              }}
            >
              <Text style={{ fontSize: 16 }}>📸 Capture</Text>
            </TouchableOpacity>
          </Animated.View>
        </>
      )}

      <Animated.View
        pointerEvents="none"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "white",
          opacity: flashAnim,
        }}
      />
    </View>
  );
}