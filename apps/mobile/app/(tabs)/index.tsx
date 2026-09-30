import { useEffect, useState } from "react";
import { FlatList, Text, TouchableOpacity, View, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { api } from "../../lib/api";

interface Audit {
  id: string;
  audit_type: string;
  audit_stage: string;
  status: string;
  auditee_name: string | null;
  start_date: string | null;
}

export default function AssignedAuditsScreen() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const router = useRouter();

  useEffect(() => {
    api.get("/audits/", { params: { status: "InProgress" } })
      .then((res) => setAudits(res.data))
      .catch(console.error);
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Assigned Audits</Text>
      <FlatList
        data={audits}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => router.push(`/audit/${item.id}`)}
          >
            <Text style={styles.cardTitle}>{item.auditee_name || "Unnamed Audit"}</Text>
            <Text style={styles.cardSub}>{item.audit_type} · {item.audit_stage}</Text>
            {item.start_date && <Text style={styles.cardDate}>{item.start_date}</Text>}
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No active audits assigned.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f9fafb", padding: 16 },
  heading: { fontSize: 24, fontWeight: "700", marginBottom: 16 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: { fontSize: 16, fontWeight: "600" },
  cardSub: { color: "#6b7280", marginTop: 2 },
  cardDate: { color: "#9ca3af", marginTop: 4, fontSize: 12 },
  empty: { textAlign: "center", color: "#9ca3af", marginTop: 32 },
});
