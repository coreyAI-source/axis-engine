import { useEffect, useState } from "react";
import {
  FlatList, Text, TouchableOpacity, View, StyleSheet, Alert
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { api } from "../../lib/api";

interface Prompt {
  id: string;
  prompt_text: string;
  prompt_type: string;
  evidence_required: boolean;
  response_status: string;
  sequence_no: number | null;
}

const RESPONSE_OPTIONS = ["C", "NC", "OBS", "FUP", "TBA", "NA"] as const;
type ResponseCode = typeof RESPONSE_OPTIONS[number];

const STATUS_COLOURS: Record<string, string> = {
  Pending: "#e5e7eb",
  C: "#d1fae5",
  NC: "#fee2e2",
  OBS: "#fef3c7",
  FUP: "#dbeafe",
  TBA: "#f3f4f6",
  NA: "#f9fafb",
};

export default function AuditPromptsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const router = useRouter();

  useEffect(() => {
    if (!id) return;
    api.get("/audit-prompts/", { params: { audit_id: id } })
      .then((res) => setPrompts(res.data))
      .catch(console.error);
  }, [id]);

  const respond = (promptId: string, status: ResponseCode) => {
    api.patch(`/audit-prompts/${promptId}/respond`, { response_status: status })
      .then((res) => {
        setPrompts((prev) =>
          prev.map((p) => (p.id === promptId ? { ...p, response_status: status } : p))
        );
        if (status === "NC") {
          Alert.alert("Finding Raised", "A finding and corrective action have been created automatically.");
        }
      })
      .catch(console.error);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Audit Prompts</Text>
      <FlatList
        data={prompts}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={[styles.card, { borderLeftColor: STATUS_COLOURS[item.response_status] || "#e5e7eb", borderLeftWidth: 4 }]}>
            <Text style={styles.promptType}>{item.prompt_type}</Text>
            <Text style={styles.promptText}>{item.prompt_text}</Text>
            {item.evidence_required && (
              <Text style={styles.evidenceFlag}>Evidence required</Text>
            )}
            <View style={styles.buttonRow}>
              {RESPONSE_OPTIONS.map((code) => (
                <TouchableOpacity
                  key={code}
                  style={[
                    styles.responseBtn,
                    item.response_status === code && styles.responseBtnActive,
                  ]}
                  onPress={() => respond(item.id, code)}
                >
                  <Text style={[
                    styles.responseBtnText,
                    item.response_status === code && styles.responseBtnTextActive,
                  ]}>{code}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No prompts generated yet.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f9fafb", padding: 16 },
  heading: { fontSize: 22, fontWeight: "700", marginBottom: 12 },
  card: {
    backgroundColor: "#fff", borderRadius: 12, padding: 16, marginBottom: 12,
    shadowColor: "#000", shadowOpacity: 0.04, shadowRadius: 4, elevation: 2,
  },
  promptType: { fontSize: 11, color: "#6b7280", fontWeight: "600", textTransform: "uppercase", marginBottom: 4 },
  promptText: { fontSize: 15, lineHeight: 22, marginBottom: 8 },
  evidenceFlag: { fontSize: 11, color: "#dc2626", fontWeight: "600", marginBottom: 8 },
  buttonRow: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  responseBtn: {
    paddingHorizontal: 10, paddingVertical: 5,
    borderRadius: 6, borderWidth: 1, borderColor: "#d1d5db",
  },
  responseBtnActive: { backgroundColor: "#1d4ed8", borderColor: "#1d4ed8" },
  responseBtnText: { fontSize: 12, fontWeight: "600", color: "#374151" },
  responseBtnTextActive: { color: "#fff" },
  empty: { textAlign: "center", color: "#9ca3af", marginTop: 32 },
});
