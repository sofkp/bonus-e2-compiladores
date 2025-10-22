import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const PARSER_SCRIPT = path.join(__dirname, "parser", "lr1_parse.py");
const WEB_PARSER_SCRIPT = path.join(__dirname, "parser", "lr1_web.py");

app.post("/api/generate-tables", (req, res) => {
  const { grammar } = req.body;

  if (!grammar) {
    return res.status(400).json({ error: "La gramática es requerida" });
  }

  console.log("📝 Generando tablas LR(1)...");
  
  const py = spawn("python3", [WEB_PARSER_SCRIPT, "tables", grammar]);
  let output = "";
  let errorOutput = "";

  py.stdout.on("data", (data) => {
    output += data.toString();
  });

  py.stderr.on("data", (data) => {
    errorOutput += data.toString();
    console.error("Python stderr:", data.toString());
  });

  py.on("close", (code) => {
    if (code !== 0) {
      console.error("❌ Error en Python, código:", code);
      console.error("Error completo:", errorOutput);
      res.status(500).json({ 
        error: errorOutput || "Error generando tablas LR(1)",
        details: `Código de salida: ${code}`
      });
    } else {
      try {
        const json = JSON.parse(output);
        console.log("✅ Tablas generadas exitosamente");
        console.log("📊 Estados DFA:", Object.keys(json.dfa?.states || {}).length);
        res.json(json);
      } catch (err) {
        console.error("❌ Error parseando JSON:", err.message);
        console.error("Salida recibida:", output);
        res.status(500).json({ 
          error: "Respuesta no válida del parser",
          details: err.message,
          rawOutput: output
        });
      }
    }
  });
});

app.post("/api/parse-string", (req, res) => {
  const { grammar, input } = req.body;

  if (!grammar || !input) {
    return res.status(400).json({ error: "Gramática y cadena son requeridas" });
  }

  console.log("🔍 Parseando cadena:", input);
  
  const py = spawn("python3", [WEB_PARSER_SCRIPT, "parse", grammar, input]);
  let output = "";
  let errorOutput = "";

  py.stdout.on("data", (data) => {
    output += data.toString();
  });

  py.stderr.on("data", (data) => {
    errorOutput += data.toString();
    console.error("Python stderr:", data.toString());
  });

  py.on("close", (code) => {
    if (code !== 0) {
      console.error("❌ Error en Python, código:", code);
      console.error("Error completo:", errorOutput);
      res.status(500).json({ 
        error: errorOutput || "Error parseando cadena",
        details: `Código de salida: ${code}`
      });
    } else {
      try {
        const json = JSON.parse(output);
        console.log("✅ Parseo completado - Resultado:", json.result);
        console.log("📈 Pasos de traza:", json.trace?.length || 0);
        res.json(json);
      } catch (err) {
        console.error("❌ Error parseando JSON:", err.message);
        console.error("Salida recibida:", output);
        res.status(500).json({ 
          error: "Respuesta no válida del parser",
          details: err.message,
          rawOutput: output
        });
      }
    }
  });
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.use((req, res) => {
  res.status(404).json({ error: "Endpoint no encontrado" });
});

app.use((err, req, res, next) => {
  console.error("💥 Error del servidor:", err);
  res.status(500).json({ 
    error: "Error interno del servidor",
    details: process.env.NODE_ENV === "development" ? err.message : undefined
  });
});

app.listen(PORT, () => {
  console.log(`🌸 Servidor LR(1) Parser corriendo en http://localhost:${PORT}`);
});