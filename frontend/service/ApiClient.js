/**
 * API Client for the AI Tour Guide FastAPI backend.
 *
 * ⚠️  Photo upload uses native `fetch` (not Axios).
 *     Axios + React Native FormData + multipart/form-data is broken:
 *     Axios overwrites the Content-Type and strips the boundary, which
 *     causes the server to reject the body as a Network Error on the
 *     client side.  `fetch` with FormData works correctly in RN.
 *
 * All other endpoints use Axios (JSON bodies, no multipart).
 */
import axios from "axios";

class ApiClient {
  /**
   * @param {string} baseUrl — FastAPI server URL, e.g. "http://192.168.1.5:8000"
   */
  constructor(baseUrl) {
    // Normalise: strip trailing slash
    this.baseUrl = baseUrl.replace(/\/$/, "");

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 15000,
      headers: { "Content-Type": "application/json" },
    });
  }

  /* ------------------------------------------------------------------ */
  /*  Session                                                            */
  /* ------------------------------------------------------------------ */

  async createSession(tourSlug = "giza-v1", language = "en") {
    const { data } = await this.client.post("/sessions", {
      tour_slug: tourSlug,
      language,
    });
    return data;
  }

  async getLivekitToken(sessionId, guestToken) {
    const { data } = await this.client.post(
      `/sessions/${sessionId}/livekit-token`,
      {},
      { headers: this._authHeaders(guestToken) }
    );
    return data;
  }

  async getSessionState(sessionId, guestToken) {
    const { data } = await this.client.get(`/sessions/${sessionId}/state`, {
      headers: this._authHeaders(guestToken),
    });
    return data;
  }

  /* ------------------------------------------------------------------ */
  /*  Photo Recognition — uses native fetch to avoid Axios/FormData bug  */
  /* ------------------------------------------------------------------ */

  /**
   * Upload a photo for asynchronous recognition (returns 202).
   *
   * Uses the global `fetch` + `FormData` instead of Axios because:
   *   • Axios in React Native does not correctly set the multipart boundary
   *     when you manually set Content-Type, causing a Network Error.
   *   • Native fetch lets FormData auto-set Content-Type with the boundary.
   *
   * @param {string} sessionId
   * @param {string} guestToken
   * @param {{ uri: string, eventId: string, idempotencyKey: string,
   *            latitude?: number, longitude?: number }} photo
   * @returns {{ recognition_id, status, request_event_id }}
   */
  async uploadPhoto(sessionId, guestToken, photo) {
    const formData = new FormData();

    // React Native FormData file entry — must be { uri, name, type }
    formData.append("file", {
      uri: photo.uri,
      name: "photo.jpg",
      type: "image/jpeg",
    });

    formData.append("event_id", photo.eventId);

    if (photo.latitude != null) {
      formData.append("latitude", String(photo.latitude));
    }
    if (photo.longitude != null) {
      formData.append("longitude", String(photo.longitude));
    }

    const url = `${this.baseUrl}/sessions/${sessionId}/photos`;

    // ⚠️  Do NOT set Content-Type manually — let fetch set it with the boundary
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${guestToken}`,
        "Idempotency-Key": photo.idempotencyKey,
        // No Content-Type here — fetch + FormData sets it automatically
      },
      body: formData,
    });

    if (!response.ok) {
      let detail = response.statusText;
      try {
        const json = await response.json();
        detail = json.detail || JSON.stringify(json);
      } catch (_) {}
      throw new Error(`Photo upload failed (${response.status}): ${detail}`);
    }

    return response.json();
  }

  /**
   * Poll the status of a recognition job.
   */
  async getRecognitionStatus(sessionId, guestToken, recognitionId) {
    const { data } = await this.client.get(
      `/sessions/${sessionId}/recognitions/${recognitionId}`,
      { headers: this._authHeaders(guestToken) }
    );
    return data;
  }

  /* ------------------------------------------------------------------ */
  /*  GPS Suggestions                                                    */
  /* ------------------------------------------------------------------ */

  async getNearbyStops(sessionId, guestToken, tourSlug, latitude, longitude) {
    const { data } = await this.client.get("/nearby-stops", {
      params: { session_id: sessionId, tour_slug: tourSlug, latitude, longitude },
      headers: this._authHeaders(guestToken),
    });
    return data;
  }

  /* ------------------------------------------------------------------ */
  /*  Observability Events                                               */
  /* ------------------------------------------------------------------ */

  async recordEvent(sessionId, guestToken, { eventId, eventType, payload = {} }) {
    const { data } = await this.client.post(
      "/events",
      { session_id: sessionId, event_id: eventId, event_type: eventType, payload },
      { headers: this._authHeaders(guestToken) }
    );
    return data;
  }

  /* ------------------------------------------------------------------ */
  /*  Helpers                                                            */
  /* ------------------------------------------------------------------ */

  _authHeaders(guestToken) {
    return { Authorization: `Bearer ${guestToken}` };
  }
}

export default ApiClient;
