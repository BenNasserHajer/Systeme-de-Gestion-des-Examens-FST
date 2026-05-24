import {
  Document,
  Page,
  StyleSheet,
  Text,
  View,
} from "@react-pdf/renderer";

type ConvocationAssignment = {
  matiere: string;
  date: string;
  heure_debut?: string;
  heure_fin?: string;
  salle?: string;
  groupe?: string;
  charge?: number;
};

type ConvocationPDFProps = {
  enseignant: {
    nom: string;
    prenom: string;
    grade?: string | null;
    departement?: string | null;
    email?: string | null;
  };
  session?: {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };
  assignments: ConvocationAssignment[];
};

const styles = StyleSheet.create({
  page: {
    padding: 32,
    fontSize: 11,
    fontFamily: "Helvetica",
    color: "#0f172a",
  },
  header: {
    marginBottom: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: "bold",
  },
  subtitle: {
    marginTop: 4,
    color: "#475569",
  },
  section: {
    marginTop: 16,
    padding: 12,
    border: "1px solid #e2e8f0",
    borderRadius: 6,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: "bold",
    marginBottom: 8,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  label: {
    color: "#64748b",
  },
  value: {
    color: "#0f172a",
  },
  assignment: {
    marginBottom: 8,
    paddingBottom: 8,
    borderBottom: "1px solid #e2e8f0",
  },
});

export function ConvocationPDF({ enseignant, session, assignments }: ConvocationPDFProps) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.title}>Convocation Surveillance</Text>
          <Text style={styles.subtitle}>
            {session?.type_session ?? "Session"} · {session?.annee_universitaire ?? "—"}
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Informations Enseignant</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Nom</Text>
            <Text style={styles.value}>{enseignant.prenom} {enseignant.nom}</Text>
          </View>
          {enseignant.grade ? (
            <View style={styles.row}>
              <Text style={styles.label}>Grade</Text>
              <Text style={styles.value}>{enseignant.grade}</Text>
            </View>
          ) : null}
          {enseignant.departement ? (
            <View style={styles.row}>
              <Text style={styles.label}>Département</Text>
              <Text style={styles.value}>{enseignant.departement}</Text>
            </View>
          ) : null}
          {enseignant.email ? (
            <View style={styles.row}>
              <Text style={styles.label}>Email</Text>
              <Text style={styles.value}>{enseignant.email}</Text>
            </View>
          ) : null}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Affectations</Text>
          {assignments.length === 0 ? (
            <Text>Aucune surveillance assignée.</Text>
          ) : (
            assignments.map((assignment, index) => (
              <View key={index} style={styles.assignment}>
                <View style={styles.row}>
                  <Text style={styles.label}>Matière</Text>
                  <Text style={styles.value}>{assignment.matiere}</Text>
                </View>
                <View style={styles.row}>
                  <Text style={styles.label}>Date</Text>
                  <Text style={styles.value}>{assignment.date}</Text>
                </View>
                <View style={styles.row}>
                  <Text style={styles.label}>Heure</Text>
                  <Text style={styles.value}>
                    {assignment.heure_debut ?? "—"} - {assignment.heure_fin ?? "—"}
                  </Text>
                </View>
                <View style={styles.row}>
                  <Text style={styles.label}>Salle</Text>
                  <Text style={styles.value}>{assignment.salle ?? "—"}</Text>
                </View>
                <View style={styles.row}>
                  <Text style={styles.label}>Groupe</Text>
                  <Text style={styles.value}>{assignment.groupe ?? "—"}</Text>
                </View>
                {assignment.charge !== undefined ? (
                  <View style={styles.row}>
                    <Text style={styles.label}>Charge</Text>
                    <Text style={styles.value}>{assignment.charge}</Text>
                  </View>
                ) : null}
              </View>
            ))
          )}
        </View>
      </Page>
    </Document>
  );
}
