import { useState, useEffect, useRef, useCallback } from "react";
import { View, Text, StyleSheet, TouchableOpacity,Image, ScrollView, ActivityIndicator, Animated} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as Speech from "expo-speech";
import * as Location from "expo-location";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import Constants from "expo-constants";

const API_BASE_URL = Constants.expoConfig?.extra?.API_BASE_URL;

const TourGuide = () => {
  const { itineraryId } = useLocalSearchParams();
  const [permission, requestPermission] = useCameraPermissions();
  const [locationPermission, setLocationPermission] = useState(null);
  const [location, setLocation] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [activeTab, setActiveTab] = useState("history");
  const cameraRef = useRef(null);
  const scanIntervalRef = useRef(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      setLocationPermission(status === "granted");
      if (status === "granted") {
        const loc = await Location.getCurrentPositionAsync({});
        setLocation(loc.coords);
      }
    })();

    return () => {
      stopScanning();
      Speech.stop();
    };
  }, []);

  
  const captureAndAnalyze = useCallback(async () => {
    if (!cameraRef.current || isLoading) return;

    try {
      setIsLoading(true);
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.5,       
        base64: true,
        skipProcessing: true,
      });

      const response = await axios.post(
        `${API_BASE_URL}/api/tour-guide/`,
        {
          image: photo.base64,
          latitude: location?.latitude || 30.0444,
          longitude: location?.longitude || 31.2357,
        },
        { timeout: 30000 }
      );

      if (response.status === 200) {
        setResult(response.data);
       
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }).start();
        
        speakText(response.data.short_summary);
      }
    } catch (error) {
      console.error("Tour guide error:", error);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, location, fadeAnim]);

  const startScanning = () => {
    setIsScanning(true);
    captureAndAnalyze();
    scanIntervalRef.current = setInterval(captureAndAnalyze, 8000); 
  };

  const stopScanning = () => {
    setIsScanning(false);
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }
  };

  
  const speakText = (text) => {
    Speech.stop();
    setIsSpeaking(true);
    Speech.speak(text, {
      language: "en-US",
      pitch: 1.0,
      rate: 0.9,
      onDone: () => setIsSpeaking(false),
      onStopped: () => setIsSpeaking(false),
    });
  };

  const speakFullNarration = () => {
    if (!result) return;
    const fullText = `${result.landmark_name}. ${result.narration.historical_background} ${result.narration.architectural_details}`;
    speakText(fullText);
  };

  const stopSpeaking = () => {
    Speech.stop();
    setIsSpeaking(false);
  };

  
  if (!permission) return <View style={styles.container} />;

  if (!permission.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>Camera access is needed for the tour guide.</Text>
        <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
          <Text style={styles.permissionButtonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      
      <CameraView ref={cameraRef} style={styles.camera} facing="back">
       
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.backBtn} onPress={() => { stopScanning(); router.back(); }}>
            <Text style={styles.backBtnText}>✕</Text>
          </TouchableOpacity>
          <Text style={styles.topTitle}>🏛️ Tour Guide</Text>
          {isLoading && <ActivityIndicator color="#D4AF37" size="small" />}
        </View>

       
        {isScanning && (
          <View style={styles.scanFrame}>
            <View style={[styles.corner, styles.topLeft]} />
            <View style={[styles.corner, styles.topRight]} />
            <View style={[styles.corner, styles.bottomLeft]} />
            <View style={[styles.corner, styles.bottomRight]} />
            <Text style={styles.scanText}>
              {isLoading ? "Analyzing..." : "Point at a landmark"}
            </Text>
          </View>
        )}

        
        {!isScanning ? (
          <TouchableOpacity style={styles.startBtn} onPress={startScanning}>
            <Text style={styles.startBtnText}>▶  Start Tour Guide</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.stopBtn} onPress={stopScanning}>
            <Text style={styles.stopBtnText}>⏹  Stop Scanning</Text>
          </TouchableOpacity>
        )}
      </CameraView>

   
      {result && (
        <Animated.View style={[styles.resultCard, { opacity: fadeAnim }]}>
          <ScrollView showsVerticalScrollIndicator={false}>
            
            <View style={styles.resultHeader}>
              <View style={{ flex: 1 }}>
                <Text style={styles.landmarkName}>{result.landmark_name}</Text>
                <Text style={styles.confidenceBadge}>
                  {result.confidence === "high" ? "✅ Identified" :
                   result.confidence === "medium" ? "🟡 Likely" : "🔴 Uncertain"}
                </Text>
              </View>
              
              <TouchableOpacity
                style={styles.speakBtn}
                onPress={isSpeaking ? stopSpeaking : speakFullNarration}
              >
                <Text style={styles.speakBtnText}>{isSpeaking ? "⏸" : "🔊"}</Text>
              </TouchableOpacity>
            </View>

           
            <View style={styles.tabs}>
              {["history", "architecture", "nearby"].map((tab) => (
                <TouchableOpacity
                  key={tab}
                  style={[styles.tab, activeTab === tab && styles.activeTab]}
                  onPress={() => setActiveTab(tab)}
                >
                  <Text style={[styles.tabText, activeTab === tab && styles.activeTabText]}>
                    {tab === "history" ? "📜 History" :
                     tab === "architecture" ? "🏛 Details" : "📍 Nearby"}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            
            <View style={styles.tabContent}>
              {activeTab === "history" && (
                <Text style={styles.narrationText}>
                  {result.narration.historical_background}
                </Text>
              )}
              {activeTab === "architecture" && (
                <Text style={styles.narrationText}>
                  {result.narration.architectural_details}
                </Text>
              )}
              {activeTab === "nearby" && (
                <View>
                  {result.narration.nearby_sites.map((site, index) => (
                    <View key={index} style={styles.nearbySite}>
                      <Text style={styles.nearbyBullet}>📍</Text>
                      <Text style={styles.nearbySiteText}>{site}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>

           
            <TouchableOpacity
              style={styles.rescanBtn}
              onPress={() => { setResult(null); fadeAnim.setValue(0); }}
            >
              <Text style={styles.rescanBtnText}>🔄 Scan Again</Text>
            </TouchableOpacity>
          </ScrollView>
        </Animated.View>
      )}
    </View>
  );
};

export default TourGuide;

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: "#000" 
},
  camera: { 
    flex: 1 
},
  permissionContainer: {
    flex: 1, 
    justifyContent: "center", 
    alignItems: "center", 
    padding: 30, 
    backgroundColor: "#111"
  },
  permissionText: { 
    color: "#fff", 
    fontSize: 16, 
    textAlign: "center", 
    marginBottom: 20, 
    fontFamily: "Poppins-Regular" 
},
  permissionButton: { 
    backgroundColor: "#D4AF37", 
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 25 },
  permissionButtonText: { 
    color: "#fff", 
    fontFamily: "Poppins-SemiBold", 
    fontSize: 15 },


  topBar: {
    flexDirection: "row", 
    alignItems: "center", 
    justifyContent: "space-between",
    paddingTop: 60, 
    paddingHorizontal: 20, 
    paddingBottom: 10,
    backgroundColor: "rgba(0,0,0,0.4)"
  },
  backBtn: { 
    width: 36, 
    height: 36, 
    borderRadius: 18, 
    backgroundColor: "rgba(255,255,255,0.2)", 
    justifyContent: "center", 
    alignItems: "center"
 },
    backBtnText: { 
    color: "#fff", 
    fontSize: 16 
},
  topTitle: { 
    color: "#fff", 
    fontFamily: "Poppins-SemiBold", 
    fontSize: 18 
},

  
  scanFrame: {
    position: "absolute", 
    top: "25%", 
    left: "10%",
    width: "80%", 
    height: "40%",
    justifyContent: "center",
    alignItems: "center",
  },
  corner: { 
    position: "absolute", 
    width: 30, 
    height: 30, 
    borderColor: "#D4AF37", 
    borderWidth: 3 },
  topLeft: { 
    top: 0, 
    left: 0, 
    borderRightWidth: 0, 
    borderBottomWidth: 0 },
  topRight: { 
    top: 0, 
    right: 0, 
    borderLeftWidth: 0, 
    borderBottomWidth: 0 },
  bottomLeft: { 
    bottom: 0, 
    left: 0, 
    borderRightWidth: 0, 
    borderTopWidth: 0 
},
  bottomRight: { 
    bottom: 0, 
    right: 0, 
    borderLeftWidth: 0, 
    borderTopWidth: 0 },
  scanText: { color: 
    "#fff", 
    fontFamily: "Poppins-Medium", 
    fontSize: 14, 
    backgroundColor: "rgba(0,0,0,0.5)", 
    paddingHorizontal: 12, 
    paddingVertical: 4, 
    borderRadius: 10 
},


  startBtn: {
    position: "absolute", 
    bottom: 40, 
    alignSelf: "center",
    backgroundColor: "#D4AF37",
     paddingHorizontal: 30, 
     paddingVertical: 14,
    borderRadius: 30, 
    flexDirection: "row", 
    alignItems: "center"
  },
  startBtnText: { 
    color: "#fff", 
    fontFamily: "Poppins-SemiBold", 
    fontSize: 16 },
  stopBtn: {
    position: "absolute",
    bottom: 40, 
    alignSelf: "center",
    backgroundColor: "rgba(220,50,50,0.85)",
    paddingHorizontal: 30,
    paddingVertical: 14,
    borderRadius: 30
  },
  stopBtnText: { 
     color: "#fff",
     fontFamily: "Poppins-SemiBold", 
     fontSize: 16 
    },

 
  resultCard: {
    position: "absolute", 
    bottom: 0, 
    left: 0,
    right: 0,
    backgroundColor: "#fff", 
    borderTopLeftRadius: 24, 
    borderTopRightRadius: 24,
    maxHeight: "55%", 
    paddingHorizontal: 20, 
    paddingTop: 16, 
    paddingBottom: 30,
    shadowColor: "#000", 
    shadowOffset: { width: 0, height: -4 }, 
    shadowOpacity: 0.15, shadowRadius: 10,
  },
  resultHeader: { flexDirection: "row", 
    alignItems: "flex-start", 
    marginBottom: 12 
},
  landmarkName: { 
    fontFamily: "Poppins-SemiBold", 
    fontSize: 18, 
    color: "#222", 
    flex: 1 
},
  confidenceBadge: { 
    fontFamily: "Poppins-Regular", 
    fontSize: 12, color: "#666", 
    marginTop: 2 
},
  speakBtn: { 
    width: 44, 
    height: 44, 
    borderRadius: 22, 
    backgroundColor: "#FFF5D6", 
    justifyContent: "center", 
    alignItems: "center" },
  speakBtnText: { fontSize: 20 },


  tabs: { 
     flexDirection: "row",
     marginBottom: 14,
     gap: 8 
    },
  tab: { 
    flex: 1, 
    paddingVertical: 8, 
    borderRadius: 20, 
    backgroundColor: "#f0f0f0", 
    alignItems: "center" 
  },
  activeTab: { 
    backgroundColor: "#D4AF37"
   },
  tabText: { 
    fontFamily: "Poppins-Medium", 
    fontSize: 12, 
    color: "#666" 
  },
  activeTabText: { 
    color: "#fff" 
  },
  tabContent: { 
    minHeight: 80 
  },
  narrationText: { 
    fontFamily: "Poppins-Regular", 
    fontSize: 14, 
    color: "#333", 
    lineHeight: 22 
  },
  nearbySite: { 
    flexDirection: "row", 
    gap: 8, 
    marginBottom: 10, 
    alignItems: "flex-start" 
  },
  nearbyBullet: { 
    fontSize: 14, 
    marginTop: 2 
  },
  nearbySiteText: { 
    fontFamily: "Poppins-Regular", 
    fontSize: 14, 
    color: "#333", 
    flex: 1, 
    lineHeight: 20 
  },

  rescanBtn: { 
    marginTop: 16, 
    alignSelf: "center", 
    paddingHorizontal: 24, 
    paddingVertical: 10, 
    borderRadius: 20, 
    borderWidth: 1.5, 
    borderColor: "#D4AF37" 
  },
  rescanBtnText: { 
    fontFamily: "Poppins-Medium", 
    fontSize: 14, 
    color: "#D4AF37" 
  },
});