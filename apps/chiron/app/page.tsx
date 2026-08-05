import Link from "next/link";

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
      <h1 style={{ fontSize: "3rem", fontWeight: 600, margin: 0, letterSpacing: "-0.02em" }}>
        Chiron
      </h1>
      <p style={{ fontSize: "1.125rem", color: "#555", marginTop: "0.75rem", marginBottom: 0 }}>
        Get ahead of the 5-series.
      </p>
      <div style={{ marginTop: "2rem" }}>
        <Link
          href="/learn"
          style={{
            display: "inline-block",
            padding: "0.75rem 1.5rem",
            borderRadius: "0.5rem",
            backgroundColor: "#111",
            color: "#fff",
            fontSize: "1rem",
            fontWeight: 500,
            textDecoration: "none"
          }}
        >
          Start learning
        </Link>
      </div>
    </main>
  );
}
