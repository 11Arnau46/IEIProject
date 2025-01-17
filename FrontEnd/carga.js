document.addEventListener("DOMContentLoaded", function () {
  const cargarBtn = document.getElementById("cargar");
  const cancelarBtn = document.getElementById("cancelar");
  const resultados = document.getElementById("resultados");
  const seleccionarTodas = document.getElementById("seleccionar_todas");
  const checkboxes = Array.from(
    document.querySelectorAll('input[name="fuente"]')
  );

  // Verificar si hay resultados guardados en sessionStorage
  const savedResults = sessionStorage.getItem("resultados");
  if (savedResults) {
    resultados.innerHTML = savedResults; // Mostrar los resultados guardados
  }

  // Evento para "Seleccionar todas"
  seleccionarTodas.addEventListener("change", function () {
    checkboxes.forEach((checkbox) => {
      checkbox.checked = seleccionarTodas.checked;
    });
  });

  // Evento para los checkboxes individuales
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      if (!this.checked) {
        seleccionarTodas.checked = false;
      } else {
        seleccionarTodas.checked = checkboxes.every((cb) => cb.checked);
      }
    });
  });

  // Evento para el botón "Cancelar"
  cancelarBtn.addEventListener("click", function () {
    checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });
    seleccionarTodas.checked = false;
    resultados.innerHTML = "";
    sessionStorage.removeItem("resultados"); // Eliminar resultados guardados
  });

  // Función para manejar el timeout
  function fetchWithTimeout(url, options, timeout) {
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Tiempo de espera excedido")), timeout)
    );
    const fetchPromise = fetch(url, options);
    return Promise.race([fetchPromise, timeoutPromise]); // La primera que resuelva se toma
  }

  // Evento para el botón "Cargar"
  document
    .getElementById("cargaForm")
    .addEventListener("submit", async function (event) {
      event.preventDefault();

      resultados.innerHTML = "<p style='color:blue;'>Cargando datos...</p>";

      // Obtener las fuentes seleccionadas
      const selectedSources = checkboxes
        .filter((checkbox) => checkbox.checked)
        .map((checkbox) => checkbox.value);

      if (seleccionarTodas.checked) {
        selectedSources.push("castilla", "valenciana", "euskadi");
      }

      if (selectedSources.length === 0) {
        resultados.innerHTML =
          '<p style="color:red;">Por favor, selecciona al menos una fuente.</p>';
        return;
      }

      const apiKey = "FUpP6o1K026VbhSuRBF0ehkKjqc5pztig_tTpn1tBeY";

      let contentTypes = [];
      if (selectedSources.includes("castilla")) contentTypes.push("xml");
      if (selectedSources.includes("valenciana")) contentTypes.push("csv");
      if (selectedSources.includes("euskadi")) contentTypes.push("json");

      if (seleccionarTodas.checked) contentTypes = ["xml", "csv", "json"];

      if (contentTypes.length === 0) {
        resultados.innerHTML =
          '<p style="color:red;">Por favor, selecciona un tipo de extractor válido.</p>';
        return;
      }

      // Primera llamada a la API (Cargar datos)
      try {
        // Mostrar mensaje de carga iniciada con tiempos estimados
        resultados.innerHTML = `
          <p style="color:green;">La carga de datos se ha iniciado correctamente. Los resultados se pueden consultar en los logs.</p>
          <p style="margin-top: 15px;">Para el caso de prueba se estima una duración de:<br>
          5 segundos para Castilla y León<br>
          5 segundos para Euskadi<br>
          3-4 minutos para Comunitat Valenciana</p>
          <p style="color:gray; font-style: italic;">La duración puede variar dependiendo de la velocidad de su internet :(</p>
        `;
        sessionStorage.setItem("resultados", resultados.innerHTML);

        // Realizar la llamada a la API sin esperar respuesta
        fetch(
          `https://localhost:8000/load?types=${contentTypes.join(
            ","
          )}&api_key=${apiKey}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${apiKey}`,
            },
          }
        );
      } catch (error) {
        console.error("Error al iniciar la carga de datos:", error);
        resultados.innerHTML =
          '<p style="color:red;">Hubo un error al iniciar la carga de datos.</p>';
        sessionStorage.setItem("resultados", resultados.innerHTML);
      }
    });

  // Evento para el botón "Borrar Almacén de Datos"
  const apiKey = "FUpP6o1K026VbhSuRBF0ehkKjqc5pztig_tTpn1tBeY";
  const borrarBtn = document.getElementById("borrar");
  borrarBtn.addEventListener("click", async function () {
    try {
      const response = await fetch(
        `https://localhost:8000/borrar-tablas?&api_key=${apiKey}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${apiKey}`, // API Key
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        resultados.innerHTML = `<p style="color:green;">${data.message}</p>`;
      } else {
        const errorData = await response.json();
        resultados.innerHTML = `<p style="color:red;">${errorData.error}</p>`;
      }
      sessionStorage.removeItem("resultados"); // Eliminar los resultados guardados después de borrar los datos
    } catch (error) {
      console.error("Error al borrar los datos:", error);
      resultados.innerHTML = `<p style="color:red;">Error al borrar los datos.</p>`;
    }
  });

  // Evento para el botón "Mostrar Logs Generales"
  const mostrarLogsBtn = document.getElementById("mostrarLogs");
  mostrarLogsBtn.addEventListener("click", async function () {
    // Obtener las fuentes seleccionadas
    const selectedSources = checkboxes
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value);

    if (seleccionarTodas.checked) {
      selectedSources.push("castilla", "valenciana", "euskadi");
    }

    if (selectedSources.length === 0) {
      resultados.innerHTML =
        '<p style="color:red;">Por favor, selecciona al menos una fuente.</p>';
      return;
    }

    // Convertir las fuentes seleccionadas a sus tipos correspondientes
    let contentTypes = [];
    if (selectedSources.includes("castilla")) contentTypes.push("xml");
    if (selectedSources.includes("valenciana")) contentTypes.push("csv");
    if (selectedSources.includes("euskadi")) contentTypes.push("json");

    if (contentTypes.length === 0) {
      resultados.innerHTML =
        '<p style="color:red;">Por favor, selecciona un tipo de extractor válido.</p>';
      return;
    }

    try {
      const response = await fetch(
        `https://localhost:8000/log/general?sources=${contentTypes.join(",")}&api_key=${apiKey}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.text();
        // Reemplazar los saltos de línea con <br> para mostrar correctamente en HTML
        const formattedData = data.replace(/\n/g, "<br>");
        resultados.innerHTML = `<pre style="text-align: left; white-space: pre-wrap;">${formattedData}</pre>`;
      } else {
        const errorData = await response.json();
        resultados.innerHTML = `<p style="color:red;">${errorData.error}</p>`;
      }
    } catch (error) {
      console.error("Error al obtener los logs:", error);
      resultados.innerHTML = `<p style="color:red;">Error al obtener los logs generales.</p>`;
    }
  });
});
