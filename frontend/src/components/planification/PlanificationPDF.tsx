import {
  Document,
  Page,
  StyleSheet,
  Text,
  View,
} from "@react-pdf/renderer";

type PlanificationExam = {
  matiere: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  salles: string[];
  groupes: string[];
  duree: number;
};

type PlanificationPDFProps = {
  session?: {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };
  section?: {
    label?: string;
    effectif?: number;
  };
  semestre?: string;
  exams: PlanificationExam[];
};

const styles = StyleSheet.create({
  page: {
    padding: 32,
    fontSize: 10,
    fontFamily: "Helvetica",
    color: "#0f172a",
  },
  header: {
    marginBottom: 20,
    borderBottom: "2px solid #4f46e5",
    paddingBottom: 12,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#4f46e5",
  },
  subtitle: {
    marginTop: 6,
    fontSize: 11,
    color: "#475569",
  },
  infoSection: {
    marginBottom: 16,
    padding: 10,
    backgroundColor: "#f8fafc",
    borderRadius: 4,
  },
  infoRow: {
    flexDirection: "row",
    marginBottom: 4,
  },
  infoLabel: {
    width: 120,
    fontWeight: "bold",
    color: "#64748b",
  },
  infoValue: {
    color: "#0f172a",
  },
  tableHeader: {
    flexDirection: "row",
    backgroundColor: "#4f46e5",
    color: "#ffffff",
    padding: 8,
    fontWeight: "bold",
    fontSize: 9,
  },
  tableRow: {
    flexDirection: "row",
    borderBottom: "1px solid #e2e8f0",
    padding: 8,
    fontSize: 9,
  },
  tableRowAlt: {
    flexDirection: "row",
    borderBottom: "1px solid #e2e8f0",
    padding: 8,
    fontSize: 9,
    backgroundColor: "#f8fafc",
  },
  colDate: {
    width: "15%",
  },
  colHeure: {
    width: "15%",
  },
  colMatiere: {
    width: "30%",
  },
  colSalles: {
    width: "25%",
  },
  colGroupes: {
    width: "15%",
  },
  footer: {
    position: "absolute",
    bottom: 32,
    left: 32,
    right: 32,
    textAlign: "center",
    fontSize: 8,
    color: "#94a3b8",
    borderTop: "1px solid #e2e8f0",
    paddingTop: 8,
  },
});

export function PlanificationPDF({ session, section, semestre, exams }: PlanificationPDFProps) {
  // Sort exams by date and time
  const sortedExams = [...exams].sort((a, b) => {
    const dateCompare = a.date.localeCompare(b.date);
    if (dateCompare !== 0) return dateCompare;
    return a.heure_debut.localeCompare(b.heure_debut);
  });

  return (
    <Document>
      <Page size="A4" orientation="landscape" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.title}>Emploi du Temps des Examens</Text>
          <Text style={styles.subtitle}>
            Université de Tunis El Manar · Faculté des Sciences de Tunis
          </Text>
        </View>

        <View style={styles.infoSection}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Session :</Text>
            <Text style={styles.infoValue}>
              {session?.type_session ?? "—"} · {session?.annee_universitaire ?? "—"}
            </Text>
          </View>
          {section?.label ? (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Section :</Text>
              <Text style={styles.infoValue}>
                {section.label} ({section.effectif ?? 0} étudiants)
              </Text>
            </View>
          ) : null}
          {semestre ? (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Semestre :</Text>
              <Text style={styles.infoValue}>{semestre}</Text>
            </View>
          ) : null}
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Nombre d'examens :</Text>
            <Text style={styles.infoValue}>{exams.length}</Text>
          </View>
        </View>

        <View style={styles.tableHeader}>
          <Text style={styles.colDate}>Date</Text>
          <Text style={styles.colHeure}>Horaire</Text>
          <Text style={styles.colMatiere}>Matière</Text>
          <Text style={styles.colSalles}>Salles</Text>
          <Text style={styles.colGroupes}>Groupes</Text>
        </View>

        {sortedExams.length === 0 ? (
          <View style={styles.tableRow}>
            <Text>Aucun examen planifié.</Text>
          </View>
        ) : (
          sortedExams.map((exam, index) => (
            <View key={index} style={index % 2 === 0 ? styles.tableRow : styles.tableRowAlt}>
              <Text style={styles.colDate}>{exam.date}</Text>
              <Text style={styles.colHeure}>
                {exam.heure_debut} - {exam.heure_fin}
              </Text>
              <Text style={styles.colMatiere}>{exam.matiere}</Text>
              <Text style={styles.colSalles}>{exam.salles.join(", ")}</Text>
              <Text style={styles.colGroupes}>{exam.groupes.join(", ")}</Text>
            </View>
          ))
        )}

        <View style={styles.footer}>
          <Text>
            Document généré le {new Date().toLocaleDateString("fr-FR")} à{" "}
            {new Date().toLocaleTimeString("fr-FR")}
          </Text>
        </View>
      </Page>
    </Document>
  );
}
