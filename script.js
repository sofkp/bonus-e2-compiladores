document.getElementById("generate").addEventListener("click", async () => {
  const grammar = document.getElementById("grammar").value;
  document.getElementById("tables").textContent = "Generando tablas...";
  const res = await fetch("/api/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grammar }),
  });
  const data = await res.json();
  document.getElementById("tables").textContent = data.result;
});

document.getElementById("parse").addEventListener("click", async () => {
  const grammar = document.getElementById("grammar").value;
  const inputString = document.getElementById("inputString").value;
  document.getElementById("trace").textContent = "Parseando...";
  const res = await fetch("/api/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grammar, inputString }),
  });
  const data = await res.json();
  document.getElementById("trace").textContent = data.result;
});
