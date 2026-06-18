import React, { useRef, useState, useEffect } from "react";
import { View, TouchableOpacity, Text, ActivityIndicator } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { router } from "expo-router";
import { useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback } from "react";

export default function CameraScreen() {
  const cameraRef = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [loading, setLoading] = useState(false);

  const API_URL = "https://12e1-8-229-115-241.ngrok-free.app/predict"; 
  const API_KEY = "secret123";

 
  useEffect(() => {
    if (!permission?.granted) {
      requestPermission();
    }
  }, [permission]);

  if (!permission?.granted) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ marginBottom: 10 }}>Camera permission required</Text>

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

  const takePicture = async () => {
    if (!cameraRef.current || loading) return;

    try {
      setLoading(true);

      
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.7,
      });

      
      const formData = new FormData();
      formData.append("file", {
        uri: photo.uri,
        type: "image/jpeg",
        name: "photo.jpg",
      });

      // 3. Send to backend
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${API_KEY}`,
        
        },
        body: formData,
      });

      const data = await res.json();

      console.log("MODEL RESULT:", data);

      
      router.replace({
        pathname: "/chatbot",
        params: {
          label: data.label,
          confidence: data.confidence,
        },
      });
    } catch (err) {
      console.log("Camera Error:", err);

      router.replace({
        pathname: "/chatbot",
        params: {
          label: "Error",
          confidence: 0,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1 }}>
   
      <CameraView ref={cameraRef} style={{ flex: 1 }} />

      
      <TouchableOpacity
        onPress={takePicture}
        style={{
          position: "absolute",
          bottom: 50,
          alignSelf: "center",
          backgroundColor: "white",
          padding: 20,
          borderRadius: 50,
          elevation: 5,
        }}
      >
        {loading ? (
          <ActivityIndicator />
        ) : (
          <Text style={{ fontSize: 16 }}>📸 Capture</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}