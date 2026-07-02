/**
 * useLiveKitVoiceAgent — Core hook for LiveKit voice agent integration.
 *
 * Manages the full lifecycle:
 *   1. Creates a tour session via FastAPI
 *   2. Fetches a LiveKit join token
 *   3. Configures mobile audio session
 *   4. Connects to the LiveKit room
 *   5. Publishes microphone audio
 *   6. Subscribes to agent audio (auto-plays)
 *   7. Tracks agent state, transcripts, and connection status
 *
 * The Python agent (agent.py) handles all voice AI logic — this hook
 * is purely a transport/UI layer.
 */
import { useState, useRef, useCallback, useEffect } from "react";
import { Room, RoomEvent, Track, ConnectionState } from "livekit-client";
import { AudioSession } from "@livekit/react-native";
import ApiClient from "../service/ApiClient";
// import { API_BASE_URL, VOICE_API_URL } from "@env";a

/** Participant attribute key used by the LiveKit Agents SDK */
const AGENT_STATE_ATTR = "lk.agent.state";
/**
 * @param {string} apiBaseUrl — FastAPI server URL (e.g. "http://192.168.1.5:8000")
 * @param {string} tourSlug  — Tour identifier (default: "giza-v1")
 * @param {string} language  — Language code: "en" or "ar-EG"
 */
export default function useLiveKitVoiceAgent(
  voiceApiUrl,
  tourSlug = "giza-v1",
  language = "en"
) {
  // ---- State ----
  const [connectionState, setConnectionState] = useState("disconnected");
  const [isAgentConnected, setIsAgentConnected] = useState(false);
  const [isMicEnabled, setIsMicEnabled] = useState(true);
  const [agentState, setAgentState] = useState("idle");
  const [transcripts, setTranscripts] = useState([]);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [error, setError] = useState(null);
  // ---- Refs ----
  const roomRef = useRef(null);
  const apiClientRef = useRef(new ApiClient(voiceApiUrl));
  // Re-create apiClient when URL changes
  useEffect(() => {
    apiClientRef.current = new ApiClient(voiceApiUrl);
  }, [voiceApiUrl]);
  /* ================================================================== */
  /*  CONNECT                                                            */
  /* ================================================================== */
  const connect = useCallback(async () => {
    try {
      setConnectionState("connecting");
      setError(null);
      setTranscripts([]);
      // 1. Create tour session
      const session = await apiClientRef.current.createSession(
        tourSlug,
        language
      );
      const info = {
        sessionId: session.session_id,
        guestToken: session.guest_session_token,
        tourSlug,
        expiresAt: session.expires_at,
      };
      setSessionInfo(info);
      // 2. Get LiveKit join token
      const tokenData = await apiClientRef.current.getLivekitToken(
        info.sessionId,
        info.guestToken
      );
      // 3. Configure audio for voice communication
      await AudioSession.configureAudio({
        android: {
          preferredOutputList: ["speaker"],
        },
        ios: {
          defaultOutput: "speaker",
        },
      });
      await AudioSession.startAudioSession();
      // 4. Create LiveKit Room
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
        // Audio-only agent — no video
        videoCaptureDefaults: { resolution: undefined },
      });
      roomRef.current = room;
      // ---- Event listeners ----
      _attachRoomListeners(room);
      // 5. Connect to the room
      await room.connect(tokenData.url, tokenData.participant_token);
      // 6. Publish microphone
      await room.localParticipant.setMicrophoneEnabled(true);
      setIsMicEnabled(true);
      setConnectionState("connected");
      // 7. Check if the agent is already present
      _detectExistingAgent(room);
    } catch (err) {
      console.error("[useLiveKitVoiceAgent] connect error:", err);
      setError(err.message || "Failed to connect");
      setConnectionState("disconnected");
    }
  }, [tourSlug, language, voiceApiUrl]);
  /* ================================================================== */
  /*  DISCONNECT                                                         */
  /* ================================================================== */
  const disconnect = useCallback(async () => {
    try {
      if (roomRef.current) {
        await roomRef.current.disconnect();
        roomRef.current = null;
      }
      await AudioSession.stopAudioSession();
    } catch (err) {
      console.error("[useLiveKitVoiceAgent] disconnect error:", err);
    } finally {
      setConnectionState("disconnected");
      setIsAgentConnected(false);
      setAgentState("idle");
      setSessionInfo(null);
    }
  }, []);
  /* ================================================================== */
  /*  TOGGLE MIC                                                         */
  /* ================================================================== */
  const toggleMic = useCallback(async () => {
    const lp = roomRef.current?.localParticipant;
    if (!lp) return;
    const next = !isMicEnabled;
    await lp.setMicrophoneEnabled(next);
    setIsMicEnabled(next);
  }, [isMicEnabled]);
  /* ================================================================== */
  /*  CLEANUP ON UNMOUNT                                                 */
  /* ================================================================== */
  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
        AudioSession.stopAudioSession().catch(() => {});
      }
    };
  }, []);
  /* ================================================================== */
  /*  PRIVATE HELPERS                                                    */
  /* ================================================================== */
  /**
   * Check whether a remote participant looks like a LiveKit Agent.
   * The Agents SDK sets participant.kind = ParticipantKind.AGENT (1).
   */
  function _isAgent(participant) {
    // kind === 1  is ParticipantKind.AGENT in livekit-client
    if (participant.kind === 1) return true;
    // Fallback: identity prefix
    const id = participant.identity || "";
    return id.startsWith("agent-") || id.startsWith("agent_");
  }
  /** Wire up all RoomEvent listeners on the Room instance. */
  function _attachRoomListeners(room) {
    room.on(RoomEvent.ConnectionStateChanged, (state) => {
      setConnectionState(state);
    });
    // Agent joins
    room.on(RoomEvent.ParticipantConnected, (participant) => {
      if (_isAgent(participant)) {
        setIsAgentConnected(true);
        _readAgentState(participant);
      }
    });
    // Agent leaves
    room.on(RoomEvent.ParticipantDisconnected, (participant) => {
      if (_isAgent(participant)) {
        setIsAgentConnected(false);
        setAgentState("idle");
      }
    });
    // Agent state changes (listening → thinking → speaking)
    room.on(
      RoomEvent.ParticipantAttributesChanged,
      (changedAttrs, participant) => {
        if (!_isAgent(participant)) return;
        const state =
          changedAttrs[AGENT_STATE_ATTR] ||
          participant.attributes?.[AGENT_STATE_ATTR];
        if (state) setAgentState(state);
      }
    );
    // Remote audio tracks auto-play on mobile once subscribed
    room.on(RoomEvent.TrackSubscribed, (track, _pub, participant) => {
      if (
        track.kind === Track.Kind.Audio &&
        participant.identity !== room.localParticipant?.identity
      ) {
        // Audio is automatically rendered on mobile — nothing to do
        console.log("[LiveKit] Agent audio track subscribed");
      }
    });
    // Transcription segments (sent by the agent SDK)
    room.on(RoomEvent.TranscriptionReceived, (segments, participant) => {
      for (const seg of segments) {
        if (!seg.final) continue; // skip interim partials
        const sender =
          participant?.identity === room.localParticipant?.identity
            ? "user"
            : "agent";
        setTranscripts((prev) => [
          ...prev,
          { sender, text: seg.text, id: seg.id },
        ]);
      }
    });
    // Room disconnected
    room.on(RoomEvent.Disconnected, () => {
      setConnectionState("disconnected");
      setIsAgentConnected(false);
      setAgentState("idle");
    });
  }
  /** Read the agent state attribute from an already-present participant. */
  function _readAgentState(participant) {
    const state = participant.attributes?.[AGENT_STATE_ATTR];
    if (state) setAgentState(state);
  }
  /** Check if the agent was already in the room before we joined. */
  function _detectExistingAgent(room) {
    for (const [, participant] of room.remoteParticipants) {
      if (_isAgent(participant)) {
        setIsAgentConnected(true);
        _readAgentState(participant);
        break;
      }
    }
  }
  /* ================================================================== */
  /*  PUBLIC API                                                         */
  /* ================================================================== */
  return {
    /** "disconnected" | "connecting" | "connected" | "reconnecting" */
    connectionState,
    /** Whether the Python voice agent is present in the room */
    isAgentConnected,
    /** Whether the local microphone is publishing */
    isMicEnabled,
    /** "idle" | "listening" | "thinking" | "speaking" */
    agentState,
    /** Array of { sender: "user"|"agent", text: string, id: string } */
    transcripts,
    /** { sessionId, guestToken, tourSlug, expiresAt } or null */
    sessionInfo,
    /** Error message string or null */
    error,
    /** Connect to a new tour session */
    connect,
    /** Disconnect and clean up */
    disconnect,
    /** Toggle microphone on/off */
    toggleMic,
  };
}
