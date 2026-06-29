/**
 * TourGuide — Immersive bilingual AI voice guide for Giza.
 *
 * Design philosophy
 * ─────────────────
 * • Feels like a field companion, not a chatbot. No Q&A bubbles.
 * • Transcript is a "narrator log" — agent words flow left-aligned like
 *   cinematic subtitles; visitor words are subtle echoes on the right.
 * • Language is automatic: Kareem mirrors whatever the visitor says.
 * • Camera is front-and-center — the guide proactively asks for it.
 *
 * Color language: deep sand (#1A1408) ground, ancient gold (#C9A84C)
 * accent, papyrus white (#F0E6C8) text — warm desert palette throughout.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Animated,
  StatusBar,
  Dimensions,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as Location from "expo-location";
import { router, useLocalSearchParams } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import useLiveKitVoiceAgent from "../../hooks/useLiveKitVoiceAgent";
import usePhotoRecognition from "../../hooks/usePhotoRecognition";

/* ====================================================================
 *  CONFIGURATION
 * ==================================================================== */
const API_BASE_URL = "http://192.168.1.5:8001";

/* ====================================================================
 *  CONSTANTS
 * ==================================================================== */
const { width: SW } = Dimensions.get("window");

// State → subtle ambient color for the orb
const ORB_COLORS = {
  idle:         "#3A3020",
  initializing: "#3A3020",
  listening:    "#1C3A28",   // deep green — I hear you
  thinking:     "#2C2010",   // ember — working
  speaking:     "#3D2C00",   // warm gold glow — narrating
};

const ORB_ACCENT = {
  idle:         "#555",
  initializing: "#666",
  listening:    "#4CAF50",
  thinking:     "#C9A84C",
  speaking:     "#C9A84C",
};

// Arabic label for each state so bilingual users always understand
const STATE_LABEL = {
  idle:         { en: "Ready",     ar: "جاهز" },
  initializing: { en: "Starting",  ar: "يشتغل" },
  listening:    { en: "Listening", ar: "بسمعك" },
  thinking:     { en: "Thinking",  ar: "بفكر" },
  speaking:     { en: "Narrating", ar: "بيحكي" },
};

/* ====================================================================
 *  COMPONENT
 * ==================================================================== */
const TourGuide = () => {
  const { itineraryId } = useLocalSearchParams();
  const [permission, requestPermission] = useCameraPermissions();
  const [location, setLocation]         = useState(null);
  const [showCamera, setShowCamera]     = useState(false);

  const cameraRef    = useRef(null);
  const scrollRef    = useRef(null);
  const pulseAnim    = useRef(new Animated.Value(1)).current;
  const fadeAnim     = useRef(new Animated.Value(0)).current;
  const cameraHintShown = useRef(false);

  /* ---- Voice agent hook ---- */
  const {
    connectionState,
    isAgentConnected,
    isMicEnabled,
    agentState,
    transcripts,
    sessionInfo,
    error: voiceError,
    connect,
    disconnect,
    toggleMic,
  } = useLiveKitVoiceAgent(API_BASE_URL);

  /* ---- Photo recognition hook ---- */
  const {
    isUploading: isPhotoUploading,
    recognitionResult,
    recognitionStatus,
    error: photoError,
    captureAndSubmit,
    reset: resetRecognition,
  } = usePhotoRecognition(API_BASE_URL);

  const isConnected  = connectionState === "connected";
  const isConnecting = connectionState === "connecting";

  /* ================================================================
   *  GPS
   * ============================================================== */
  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === "granted") {
        const loc = await Location.getCurrentPositionAsync({});
        setLocation(loc.coords);
      }
    })();
  }, []);

  /* ================================================================
   *  Fade-in on connect
   * ============================================================== */
  useEffect(() => {
    if (isConnected) {
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }).start();
    } else {
      fadeAnim.setValue(0);
    }
  }, [isConnected]);

  /* ================================================================
   *  Pulse when speaking
   * ============================================================== */
  useEffect(() => {
    if (agentState === "speaking") {
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.45, duration: 900, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1,    duration: 900, useNativeDriver: true }),
        ])
      );
      pulse.start();
      return () => pulse.stop();
    }
    pulseAnim.setValue(1);
  }, [agentState]);

  /* ================================================================
   *  Auto-scroll transcript
   * ============================================================== */
  useEffect(() => {
    if (scrollRef.current && transcripts.length > 0) {
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 120);
    }
  }, [transcripts]);

  /* ================================================================
   *  Show camera hint after 3rd agent transcript
   * ============================================================== */
  useEffect(() => {
    const agentLines = transcripts.filter(t => t.sender === "agent");
    if (agentLines.length >= 2 && !cameraHintShown.current && isConnected) {
      cameraHintShown.current = true;
      // No-op — the agent handles the verbal invite; we just pulse the button
    }
  }, [transcripts, isConnected]);

  /* ================================================================
   *  Handlers
   * ============================================================== */
  const handlePhotoCapture = useCallback(async () => {
    if (!sessionInfo) return;
    await captureAndSubmit(
      cameraRef,
      sessionInfo.sessionId,
      sessionInfo.guestToken,
      location
    );
    setShowCamera(false);
  }, [sessionInfo, location, captureAndSubmit]);

  const handleDisconnect = useCallback(async () => {
    await disconnect();
    router.back();
  }, [disconnect]);

  /* ================================================================
   *  Permissions screen
   * ============================================================== */
  if (!permission) return <View style={s.root} />;

  if (!permission.granted) {
    return (
      <View style={s.permScreen}>
        <StatusBar barStyle="light-content" />
        <Text style={s.permEmoji}>📸</Text>
        <Text style={s.permTitle}>Camera Access Needed{"\n"}مطلوب إذن الكاميرا</Text>
        <Text style={s.permBody}>
          Point your camera at any monument and your guide will explain it.
          {"\n"}صوّر أي معلم وسيشرح لك المرشد ما تراه.
        </Text>
        <TouchableOpacity style={s.goldBtn} onPress={requestPermission}>
          <Text style={s.goldBtnText}>Allow Camera · اسمح بالكاميرا</Text>
        </TouchableOpacity>
      </View>
    );
  }

  /* ================================================================
   *  Derive label in both languages
   * ============================================================== */
  const stateLabels = STATE_LABEL[agentState] || STATE_LABEL.idle;
  const stateLabel  = `${stateLabels.en} · ${stateLabels.ar}`;

  /* ================================================================
   *  RENDER
   * ============================================================== */
  return (
    <View style={s.root}>
      <StatusBar barStyle="light-content" />

      {/* ── Top bar ─────────────────────────────────────────────── */}
      <View style={s.topBar}>
        <TouchableOpacity style={s.closeBtn} onPress={handleDisconnect}>
          <Text style={s.closeBtnText}>✕</Text>
        </TouchableOpacity>

        <View style={s.topCenter}>
          <Text style={s.topTitle}>Giza · الجيزة</Text>
          <View style={s.statusRow}>
            <View style={[s.dot, {
              backgroundColor: isConnected
                ? isAgentConnected ? "#4CAF50" : "#C9A84C"
                : isConnecting    ? "#C9A84C"           : "#555",
            }]} />
            <Text style={s.statusTxt}>
              {isConnected
                ? isAgentConnected ? "Kareem is with you · كريم معاك" : "Waiting for guide…"
                : isConnecting ? "Connecting…"
                : "Offline"}
            </Text>
          </View>
        </View>

        {/* Mic toggle — top-right */}
        {isConnected && (
          <TouchableOpacity style={[s.micChip, !isMicEnabled && s.micChipMuted]} onPress={toggleMic}>
            <Text style={s.micChipIcon}>{isMicEnabled ? "🎤" : "🔇"}</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* ================================================================
       *  NOT CONNECTED — Start screen
       * ============================================================== */}
      {!isConnected && !isConnecting ? (
        <View style={s.startScreen}>
          {/* Ambient background glow */}
          <View style={s.startGlow} />

          <View style={s.startHero}>
            <Text style={s.startEmoji}>🏛</Text>
            <Text style={s.startTitle}>Your guide awaits</Text>
            <Text style={s.startTitleAr}>مرشدك في انتظارك</Text>
            <Text style={s.startSub}>
              Speak naturally in English or Arabic.{"\n"}
              كلّم كريم بالعربي أو بالإنجليزي — هيفهمك.
            </Text>
          </View>

          <TouchableOpacity style={s.startBtn} onPress={connect}>
            <Text style={s.startBtnText}>Begin the tour · ابدأ الجولة</Text>
          </TouchableOpacity>

          {voiceError && (
            <Text style={s.errorTxt}>⚠ {voiceError}</Text>
          )}

          <View style={s.featureRow}>
            {[
              ["🎙", "Voice in EN & AR"],
              ["📷", "Landmark camera"],
              ["📍", "GPS-aware"],
            ].map(([icon, label]) => (
              <View key={label} style={s.featureChip}>
                <Text style={s.featureIcon}>{icon}</Text>
                <Text style={s.featureLabel}>{label}</Text>
              </View>
            ))}
          </View>
        </View>

      ) : (
      /* ================================================================
       *  CONNECTED — Active tour
       * ============================================================== */
        <Animated.View style={[s.tourScreen, { opacity: isConnecting ? 0.6 : fadeAnim }]}>

          {/* ── Agent orb ──────────────────────────────────────── */}
          <View style={s.orbSection}>
            <Animated.View
              style={[
                s.orbOuter,
                { backgroundColor: ORB_COLORS[agentState] || ORB_COLORS.idle,
                  transform: [{ scale: pulseAnim }] }
              ]}
            >
              <View style={[s.orbInner, { borderColor: ORB_ACCENT[agentState] || "#555" }]}>
                <Text style={s.orbEmoji}>
                  {agentState === "speaking"  ? "🗣" :
                   agentState === "thinking"  ? "💭" :
                   agentState === "listening" ? "👂" : "🏛"}
                </Text>
              </View>
            </Animated.View>
            <Text style={s.orbLabel}>{stateLabel}</Text>
            {isConnecting && (
              <ActivityIndicator color="#C9A84C" size="small" style={{ marginTop: 6 }} />
            )}
          </View>

          {/* ── Camera overlay ─────────────────────────────────── */}
          {showCamera && (
            <View style={s.cameraOverlay}>
              <CameraView ref={cameraRef} style={s.cameraFill} facing="back">
                {/* Corner frame */}
                <View style={s.frameContainer}>
                  {["tl","tr","bl","br"].map(pos => (
                    <View key={pos} style={[s.corner, s[pos]]} />
                  ))}
                  <Text style={s.frameTxt}>
                    {isPhotoUploading
                      ? "Analyzing… · بحلل…"
                      : "Aim at a landmark · صوّر معلمًا"}
                  </Text>
                </View>

                {/* Controls */}
                <View style={s.cameraControls}>
                  <TouchableOpacity
                    style={s.shutterBtn}
                    onPress={handlePhotoCapture}
                    disabled={isPhotoUploading}
                  >
                    {isPhotoUploading
                      ? <ActivityIndicator color="#C9A84C" size="small" />
                      : <View style={s.shutterInner} />
                    }
                  </TouchableOpacity>
                  <TouchableOpacity style={s.closeCamBtn} onPress={() => setShowCamera(false)}>
                    <Text style={s.closeCamTxt}>✕  Close · اغلق</Text>
                  </TouchableOpacity>
                </View>
              </CameraView>
            </View>
          )}

          {/* ── Transcript / narration log ─────────────────────── */}
          <ScrollView
            ref={scrollRef}
            style={s.transcript}
            contentContainerStyle={s.transcriptInner}
            showsVerticalScrollIndicator={false}
          >
            {transcripts.length === 0 && isConnected && (
              <View style={s.emptyLog}>
                <Text style={s.emptyLogIcon}>🏺</Text>
                <Text style={s.emptyLogTxt}>
                  {isAgentConnected
                    ? "Kareem is about to speak…\nكريم على وشك يتكلم…"
                    : "Connecting to your guide…\nجاري الاتصال بمرشدك…"}
                </Text>
              </View>
            )}

            {transcripts.map((item, idx) => {
              const isAgent = item.sender === "agent";
              return (
                <View
                  key={item.id || `t${idx}`}
                  style={[s.bubble, isAgent ? s.agentBubble : s.userBubble]}
                >
                  {isAgent && (
                    <Text style={s.bubbleSender}>🏛 Kareem</Text>
                  )}
                  <Text style={[s.bubbleText, isAgent ? s.agentText : s.userText]}>
                    {item.text}
                  </Text>
                </View>
              );
            })}
          </ScrollView>

          {/* ── Recognition result ─────────────────────────────── */}
          {recognitionResult && (
            <View style={s.recCard}>
              <View style={s.recHeader}>
                <Text style={s.recTitle}>📸 Identified · تم التعرف</Text>
                <TouchableOpacity onPress={resetRecognition}>
                  <Text style={s.recDismiss}>✕</Text>
                </TouchableOpacity>
              </View>
              <Text style={s.recBody}>
                {recognitionResult.recognition_summary || "Recognition complete"}
              </Text>
              {recognitionResult.confidence != null && (
                <View style={[
                  s.confBadge,
                  { backgroundColor:
                      recognitionResult.confidence > 0.7 ? "#1B4D2E" :
                      recognitionResult.confidence > 0.4 ? "#3D2C00" : "#4D1111" }
                ]}>
                  <Text style={s.confTxt}>
                    {Math.round(recognitionResult.confidence * 100)}% match
                  </Text>
                </View>
              )}
            </View>
          )}

          {/* ── Photo error ────────────────────────────────────── */}
          {photoError && (
            <View style={s.errCard}>
              <Text style={s.errTxt}>⚠ {photoError}</Text>
              <TouchableOpacity onPress={resetRecognition}>
                <Text style={s.errDismiss}>Dismiss · اغلق</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* ── Bottom controls ─────────────────────────────────── */}
          <View style={s.bottomBar}>
            {/* Camera — central, always gold */}
            <TouchableOpacity
              style={[s.cameraBtn, (!isConnected || showCamera) && s.btnDisabled]}
              onPress={() => setShowCamera(true)}
              disabled={!isConnected || showCamera}
            >
              <Text style={s.cameraBtnIcon}>📷</Text>
              <Text style={s.cameraBtnLabel}>Show guide · أرني</Text>
            </TouchableOpacity>

            {/* End */}
            <TouchableOpacity style={s.endBtn} onPress={handleDisconnect}>
              <Text style={s.endBtnIcon}>⏹</Text>
              <Text style={s.endBtnLabel}>End · انهِ</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      )}
    </View>
  );
};

export default TourGuide;

/* ====================================================================
 *  STYLES
 *  Palette:  ground #1A1408 · deep #100D04 · gold #C9A84C
 *            papyrus #F0E6C8 · muted #8A7D60
 * ==================================================================== */
const GOLD   = "#C9A84C";
const GROUND = "#1A1408";
const DEEP   = "#100D04";
const PAPYRUS = "#F0E6C8";
const MUTED  = "#8A7D60";
const RED    = "#C0392B";

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: DEEP },

  /* ── Permission ── */
  permScreen: {
    flex: 1, backgroundColor: DEEP,
    alignItems: "center", justifyContent: "center", padding: 32,
  },
  permEmoji: { fontSize: 52, marginBottom: 16 },
  permTitle: {
    color: PAPYRUS, fontSize: 18, textAlign: "center",
    fontFamily: "Poppins-SemiBold", marginBottom: 10, lineHeight: 26,
  },
  permBody: {
    color: MUTED, fontSize: 14, textAlign: "center",
    fontFamily: "Poppins-Regular", lineHeight: 22, marginBottom: 28,
  },
  goldBtn: {
    backgroundColor: GOLD, paddingHorizontal: 28, paddingVertical: 14,
    borderRadius: 28,
  },
  goldBtnText: {
    color: DEEP, fontFamily: "Poppins-SemiBold", fontSize: 14,
  },

  /* ── Top bar ── */
  topBar: {
    flexDirection: "row", alignItems: "center",
    paddingTop: 54, paddingHorizontal: 18, paddingBottom: 12,
    backgroundColor: "rgba(16,13,4,0.92)",
    borderBottomWidth: 1, borderBottomColor: "rgba(201,168,76,0.12)",
  },
  closeBtn: {
    width: 34, height: 34, borderRadius: 17,
    backgroundColor: "rgba(255,255,255,0.08)",
    justifyContent: "center", alignItems: "center",
  },
  closeBtnText: { color: PAPYRUS, fontSize: 15 },
  topCenter: { flex: 1, alignItems: "center" },
  topTitle: {
    color: GOLD, fontFamily: "Poppins-SemiBold", fontSize: 16, letterSpacing: 0.6,
  },
  statusRow: { flexDirection: "row", alignItems: "center", gap: 5, marginTop: 2 },
  dot: { width: 7, height: 7, borderRadius: 4 },
  statusTxt: { color: MUTED, fontSize: 10, fontFamily: "Poppins-Regular" },
  micChip: {
    width: 34, height: 34, borderRadius: 17,
    backgroundColor: "rgba(201,168,76,0.12)",
    justifyContent: "center", alignItems: "center",
  },
  micChipMuted: { backgroundColor: "rgba(192,57,43,0.18)" },
  micChipIcon: { fontSize: 16 },

  /* ── Start screen ── */
  startScreen: {
    flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: 28,
  },
  startGlow: {
    position: "absolute", width: 320, height: 320,
    borderRadius: 160, backgroundColor: "rgba(201,168,76,0.04)",
    top: "25%",
  },
  startHero: { alignItems: "center", marginBottom: 40 },
  startEmoji: { fontSize: 72, marginBottom: 12 },
  startTitle: {
    color: PAPYRUS, fontSize: 26, fontFamily: "Poppins-SemiBold", marginBottom: 2,
  },
  startTitleAr: {
    color: GOLD, fontSize: 20, fontFamily: "Poppins-Medium", marginBottom: 14,
  },
  startSub: {
    color: MUTED, fontSize: 14, textAlign: "center",
    fontFamily: "Poppins-Regular", lineHeight: 22,
  },
  startBtn: {
    backgroundColor: GOLD, paddingHorizontal: 36, paddingVertical: 16,
    borderRadius: 30, marginBottom: 24,
    shadowColor: GOLD, shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.28, shadowRadius: 10, elevation: 6,
  },
  startBtnText: {
    color: DEEP, fontFamily: "Poppins-SemiBold", fontSize: 17,
  },
  errorTxt: {
    color: RED, fontSize: 12, fontFamily: "Poppins-Regular",
    textAlign: "center", marginBottom: 16,
  },
  featureRow: {
    flexDirection: "row", gap: 12, marginTop: 12,
  },
  featureChip: {
    alignItems: "center", backgroundColor: "rgba(201,168,76,0.07)",
    paddingHorizontal: 12, paddingVertical: 8, borderRadius: 12,
  },
  featureIcon: { fontSize: 18, marginBottom: 2 },
  featureLabel: { color: MUTED, fontSize: 10, fontFamily: "Poppins-Regular" },

  /* ── Tour screen ── */
  tourScreen: { flex: 1 },

  /* ── Orb ── */
  orbSection: {
    alignItems: "center", paddingVertical: 22,
    borderBottomWidth: 1, borderBottomColor: "rgba(201,168,76,0.06)",
  },
  orbOuter: {
    width: 76, height: 76, borderRadius: 38,
    justifyContent: "center", alignItems: "center",
  },
  orbInner: {
    width: 62, height: 62, borderRadius: 31,
    borderWidth: 1.5,
    justifyContent: "center", alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.35)",
  },
  orbEmoji: { fontSize: 26 },
  orbLabel: {
    color: MUTED, fontSize: 11, fontFamily: "Poppins-Medium",
    marginTop: 7, letterSpacing: 0.4,
  },

  /* ── Camera ── */
  cameraOverlay: {
    position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
    zIndex: 20, backgroundColor: "#000",
  },
  cameraFill: { flex: 1 },
  frameContainer: {
    position: "absolute", top: "22%", left: "8%",
    width: "84%", height: "44%",
    justifyContent: "center", alignItems: "center",
  },
  corner: { position: "absolute", width: 28, height: 28, borderColor: GOLD, borderWidth: 2.5 },
  tl: { top: 0, left: 0, borderRightWidth: 0, borderBottomWidth: 0 },
  tr: { top: 0, right: 0, borderLeftWidth: 0, borderBottomWidth: 0 },
  bl: { bottom: 0, left: 0, borderRightWidth: 0, borderTopWidth: 0 },
  br: { bottom: 0, right: 0, borderLeftWidth: 0, borderTopWidth: 0 },
  frameTxt: {
    color: PAPYRUS, fontFamily: "Poppins-Medium", fontSize: 13,
    backgroundColor: "rgba(0,0,0,0.65)",
    paddingHorizontal: 14, paddingVertical: 5, borderRadius: 10,
  },
  cameraControls: {
    position: "absolute", bottom: 44, alignSelf: "center", alignItems: "center", gap: 14,
  },
  shutterBtn: {
    width: 68, height: 68, borderRadius: 34,
    borderWidth: 3, borderColor: GOLD,
    backgroundColor: "rgba(255,255,255,0.08)",
    justifyContent: "center", alignItems: "center",
  },
  shutterInner: { width: 52, height: 52, borderRadius: 26, backgroundColor: GOLD },
  closeCamBtn: {
    backgroundColor: "rgba(255,255,255,0.12)",
    paddingHorizontal: 20, paddingVertical: 8, borderRadius: 16,
  },
  closeCamTxt: { color: PAPYRUS, fontFamily: "Poppins-Medium", fontSize: 12 },

  /* ── Transcript ── */
  transcript: { flex: 1 },
  transcriptInner: { padding: 16, paddingBottom: 8 },
  emptyLog: { alignItems: "center", paddingTop: 32 },
  emptyLogIcon: { fontSize: 36, marginBottom: 10 },
  emptyLogTxt: {
    color: MUTED, fontSize: 13, textAlign: "center",
    fontFamily: "Poppins-Regular", lineHeight: 22,
  },

  /* Agent bubble — left-aligned, no label needed (Kareem speaks) */
  bubble: { marginBottom: 10, maxWidth: "90%" },
  agentBubble: { alignSelf: "flex-start" },
  userBubble: { alignSelf: "flex-end" },
  bubbleSender: {
    color: GOLD, fontSize: 10, fontFamily: "Poppins-Medium",
    marginBottom: 3, letterSpacing: 0.5,
  },
  bubbleText: { fontSize: 15, lineHeight: 23, fontFamily: "Poppins-Regular" },
  agentText: {
    color: PAPYRUS,
    /* Narrative text — no bubble background, reads like captions */
  },
  userText: {
    color: MUTED, fontSize: 13, fontStyle: "italic",
    backgroundColor: "rgba(201,168,76,0.07)",
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12,
    borderBottomRightRadius: 3,
  },

  /* ── Recognition card ── */
  recCard: {
    marginHorizontal: 16, marginBottom: 8,
    backgroundColor: "rgba(201,168,76,0.07)",
    borderRadius: 14, padding: 14,
    borderWidth: 1, borderColor: "rgba(201,168,76,0.18)",
  },
  recHeader: {
    flexDirection: "row", justifyContent: "space-between",
    alignItems: "center", marginBottom: 6,
  },
  recTitle: { color: GOLD, fontFamily: "Poppins-SemiBold", fontSize: 13 },
  recDismiss: { color: MUTED, fontSize: 16, padding: 4 },
  recBody: { color: PAPYRUS, fontFamily: "Poppins-Regular", fontSize: 13, lineHeight: 20 },
  confBadge: {
    alignSelf: "flex-start", marginTop: 8,
    paddingHorizontal: 10, paddingVertical: 3, borderRadius: 8,
  },
  confTxt: { color: PAPYRUS, fontSize: 11, fontFamily: "Poppins-Medium" },

  /* ── Error card ── */
  errCard: {
    marginHorizontal: 16, marginBottom: 8,
    backgroundColor: "rgba(192,57,43,0.1)",
    borderRadius: 12, padding: 12,
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
  },
  errTxt: { color: RED, fontSize: 12, fontFamily: "Poppins-Regular", flex: 1 },
  errDismiss: { color: RED, fontFamily: "Poppins-Medium", fontSize: 12, paddingLeft: 12 },

  /* ── Bottom bar ── */
  bottomBar: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingVertical: 16,
    paddingBottom: 34,
    paddingHorizontal: 24,
    backgroundColor: "rgba(16,13,4,0.9)",
    borderTopWidth: 1, borderTopColor: "rgba(201,168,76,0.08)",
  },

  /* Camera button — primary action, centered & large */
  cameraBtn: {
    alignItems: "center", justifyContent: "center",
    width: 80, height: 80, borderRadius: 40,
    backgroundColor: GOLD,
    shadowColor: GOLD, shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.35, shadowRadius: 8, elevation: 6,
  },
  cameraBtnIcon: { fontSize: 26 },
  cameraBtnLabel: {
    color: DEEP, fontSize: 9, fontFamily: "Poppins-SemiBold", marginTop: 2,
  },

  endBtn: {
    alignItems: "center", justifyContent: "center",
    width: 56, height: 56, borderRadius: 28,
    backgroundColor: "rgba(192,57,43,0.14)",
  },
  endBtnIcon: { fontSize: 20 },
  endBtnLabel: { color: RED, fontSize: 9, fontFamily: "Poppins-Medium", marginTop: 2 },

  btnDisabled: { opacity: 0.4 },
});