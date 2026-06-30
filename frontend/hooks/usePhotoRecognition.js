/**
 * usePhotoRecognition — Async photo recognition hook.
 *
 * Fixes applied vs original:
 *   1. Camera capture uses `takePictureAsync` with `skipProcessing: false`
 *      on Android (skipProcessing: true causes empty/corrupt URIs on some
 *      Android devices).
 *   2. Validates that the photo URI exists before uploading.
 *   3. Better error messages that distinguish capture vs upload failures.
 *   4. Poll timeout extended to 90 s (recognition can be slow on cold start).
 *   5. Re-creates ApiClient when apiBaseUrl changes (was already there, kept).
 */
import { useState, useRef, useCallback, useEffect } from "react";
import { Platform } from "react-native";
import ApiClient from "../service/ApiClient";

const MAX_POLL_WAIT_MS = 90_000;   // 90 s — allow for cold AI start
const POLL_INTERVAL_MS = 2_000;

export default function usePhotoRecognition(apiBaseUrl) {
  const [isUploading, setIsUploading]           = useState(false);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [recognitionStatus, setRecognitionStatus] = useState("idle");
  const [error, setError]                       = useState(null);

  const apiClientRef  = useRef(new ApiClient(apiBaseUrl));
  const pollTimerRef  = useRef(null);

  useEffect(() => {
    apiClientRef.current = new ApiClient(apiBaseUrl);
  }, [apiBaseUrl]);

  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  /* ================================================================== */
  /*  CAPTURE AND SUBMIT                                                 */
  /* ================================================================== */

  const captureAndSubmit = useCallback(
    async (cameraRef, sessionId, guestToken, location) => {
      // ── Guard: ref and session must exist ──────────────────────────
      if (!cameraRef?.current) {
        console.warn("[usePhotoRecognition] cameraRef is not ready");
        setError("Camera is not ready — please try again.");
        setRecognitionStatus("error");
        return;
      }
      if (!sessionId || !guestToken) {
        console.warn("[usePhotoRecognition] missing sessionId or guestToken");
        setError("Session not ready — please reconnect.");
        setRecognitionStatus("error");
        return;
      }

      try {
        setIsUploading(true);
        setRecognitionStatus("capturing");
        setError(null);
        setRecognitionResult(null);

        // ── Take photo ──────────────────────────────────────────────
        // skipProcessing must be false on Android — true can produce
        // an unreadable file on certain devices/Expo versions.
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.6,
          base64: false,
          skipProcessing: Platform.OS === "ios", // safe on iOS, risky on Android
          exif: false,
        });

        if (!photo?.uri) {
          throw new Error("Camera returned an empty photo — please try again.");
        }

        console.log("[usePhotoRecognition] captured photo:", photo.uri);
        setRecognitionStatus("uploading");

        const eventId       = _generateId("evt");
        const idempotencyKey = _generateId("idem");

        // ── Upload ─────────────────────────────────────────────────
        const uploadResult = await apiClientRef.current.uploadPhoto(
          sessionId,
          guestToken,
          {
            uri: photo.uri,
            eventId,
            idempotencyKey,
            latitude:  location?.latitude,
            longitude: location?.longitude,
          }
        );

        console.log("[usePhotoRecognition] upload accepted:", uploadResult.recognition_id);
        setRecognitionStatus("processing");

        // ── Poll ───────────────────────────────────────────────────
        _startPolling(sessionId, guestToken, uploadResult.recognition_id);

      } catch (err) {
        console.error("[usePhotoRecognition] captureAndSubmit error:", err);

        // Surface a readable message
        const msg =
          err?.message?.includes("Network")
            ? "Could not reach the server — check your Wi-Fi and the API_BASE_URL."
            : err?.message || "Photo capture failed.";

        setError(msg);
        setRecognitionStatus("error");
        setIsUploading(false);
      }
    },
    []
  );

  /* ================================================================== */
  /*  RESET                                                              */
  /* ================================================================== */

  const reset = useCallback(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setIsUploading(false);
    setRecognitionResult(null);
    setRecognitionStatus("idle");
    setError(null);
  }, []);

  /* ================================================================== */
  /*  PRIVATE — polling                                                  */
  /* ================================================================== */

  function _startPolling(sessionId, guestToken, recognitionId) {
    const startTime = Date.now();

    pollTimerRef.current = setInterval(async () => {
      if (Date.now() - startTime > MAX_POLL_WAIT_MS) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
        setRecognitionStatus("timeout");
        setError("Recognition is taking too long — please try again.");
        setIsUploading(false);
        return;
      }

      try {
        const status = await apiClientRef.current.getRecognitionStatus(
          sessionId,
          guestToken,
          recognitionId
        );

        if (status.status === "completed") {
          clearInterval(pollTimerRef.current);
          pollTimerRef.current = null;
          setRecognitionResult(status);
          setRecognitionStatus("completed");
          setIsUploading(false);

        } else if (status.status === "failed") {
          clearInterval(pollTimerRef.current);
          pollTimerRef.current = null;
          setRecognitionStatus("failed");
          setError(status.error_code || "Recognition failed on the server.");
          setIsUploading(false);
        }
        // "pending" → keep polling

      } catch (pollErr) {
        // Transient network hiccup — don't stop, just warn
        console.warn("[usePhotoRecognition] poll error:", pollErr.message);
      }
    }, POLL_INTERVAL_MS);
  }

  function _generateId(prefix) {
    const ts   = Date.now().toString(36);
    const rand = Math.random().toString(36).slice(2, 10);
    return `${prefix}_${ts}_${rand}`;
  }

  /* ================================================================== */
  /*  PUBLIC API                                                         */
  /* ================================================================== */

  return {
    isUploading,
    recognitionResult,
    /** "idle"|"capturing"|"uploading"|"processing"|"completed"|"failed"|"timeout"|"error" */
    recognitionStatus,
    error,
    captureAndSubmit,
    reset,
  };
}