export default function Home() {
  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "2rem",
        maxWidth: "42rem",
        margin: "0 auto"
      }}
    >
      <h1 style={{ fontSize: "3rem", fontWeight: 600, margin: 0 }}>Chiron</h1>
      <p style={{ fontSize: "1.125rem", color: "#555", marginTop: "0.75rem" }}>
        Get ahead of the 5-series.
      </p>
    </main>
  );
}
