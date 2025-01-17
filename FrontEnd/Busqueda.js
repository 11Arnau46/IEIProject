document.addEventListener("DOMContentLoaded", async () => {
  console.log("El archivo JavaScript se ha cargado correctamente.");

  const mapa = L.map("mapa").setView([40.4168, -3.7038], 6); // Centro de España
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa);

  let markers = [];
  let datos = []; // Variable para almacenar los datos cargados
  const localidadInput = document.getElementById("localidad");
  const provinciaInput = document.getElementById("provincia");
  const postalInput = document.getElementById("codigo_postal");
  const buscarBtn = document.getElementById("buscar");
  const tipoSelect = document.getElementById("tipo");
  // Función para limpiar los marcadores del mapa
  function limpiarMapa() {
    markers.forEach((marker) => marker.remove());
    markers = [];
  }

  // Función para ordenar la tabla por una columna
  function ordenarTabla(columna, orden) {
    const tabla = document
      .getElementById("tabla-resultados")
      .querySelector("tbody");
    const filas = Array.from(tabla.rows);

    filas.sort((filaA, filaB) => {
      const textoA = filaA.cells[columna].textContent.trim().toLowerCase();
      const textoB = filaB.cells[columna].textContent.trim().toLowerCase();

      if (textoA < textoB) {
        return orden === "asc" ? -1 : 1;
      }
      if (textoA > textoB) {
        return orden === "asc" ? 1 : -1;
      }
      return 0;
    });

    filas.forEach((fila) => tabla.appendChild(fila));
  }

  // Función para agregar o quitar el espacio dependiendo de la visibilidad de las sugerencias
  function ajustarEspacio(suggestionsList, input) {
    const formGroup = input.closest(".form-group"); // Selecciona el contenedor del campo de entrada
    const form = document.querySelector(".form");
    if (suggestionsList.children.length > 0) {
      formGroup.classList.add("margin-bottom-100"); // Añadir espacio
    } else {
      formGroup.classList.remove("margin-bottom-100"); // Quitar espacio
    }
  }

  // Función para mostrar sugerencias en los campos de texto
  function mostrarSugerencias(input, key, suggestionsId) {
    const value = input.value.trim().toLowerCase();
    const suggestionsList = document.getElementById(suggestionsId);
    suggestionsList.innerHTML = "";

    if (value.length === 0) {
      suggestionsList.style.display = "none";
      return;
    }

    const uniqueSuggestions = [...new Set(datos.map((d) => d[key]))];

    // Ordenar por prioridad
    const suggestions = uniqueSuggestions
      .map((s) => ({
        text: s,
        lower: s.toLowerCase(),
        priority:
          s.toLowerCase() === value
            ? 1 // Coincidencia exacta
            : s.toLowerCase().startsWith(value)
            ? 2 // Empieza con el input
            : s.toLowerCase().includes(value)
            ? 3
            : 4, // Contiene el input
      }))
      .filter((s) => s.priority < 4) // Excluir las que no coinciden en absoluto
      .sort((a, b) => a.priority - b.priority || a.text.localeCompare(b.text));

    if (suggestions.length === 0) {
      suggestionsList.style.display = "none";
      return;
    }

    suggestions.forEach(({ text }) => {
      const li = document.createElement("li");
      li.textContent = text;
      li.addEventListener("click", () => {
        input.value = text;
        suggestionsList.innerHTML = "";
        suggestionsList.style.display = "none";
      });
      suggestionsList.appendChild(li);
    });

    suggestionsList.style.display = "block";
  }

  // Cerrar sugerencias cuando se pierde el foco
  document.addEventListener("click", (e) => {
    if (!e.target.matches("input, #" + suggestionsId + " li")) {
      document.getElementById(suggestionsId).style.display = "none";
    }
  });

  // Función para obtener los datos desde la API
  async function obtenerDatosDesdeAPI(filtros) {
    try {
      const queryParams = new URLSearchParams(filtros).toString();
      const response = await fetch(
        `http://localhost:5001/api/monumentos?${queryParams}`
      );
      if (!response.ok) {
        throw new Error("Error al obtener los datos desde la API");
      }
      return await response.json();
    } catch (error) {
      console.error("Error al cargar los datos desde la API:", error);
      return [];
    }
  }

  // Mostrar todos los resultados en la tabla y el mapa
  function mostrarResultados(resultados) {
    const tabla = document
      .getElementById("tabla-resultados")
      .querySelector("tbody");
    tabla.innerHTML = "";

    limpiarMapa(); // Limpiar los marcadores previos

    resultados.forEach((d) => {
      const fila = `<tr>
          <td>${d.nombre_monumento}</td>
          <td>${d.tipo_monumento}</td>
          <td>${d.direccion}</td>
          <td>${d.nombre_localidad}</td>
          <td>${d.codigo_postal}</td>
          <td>${d.nombre_provincia}</td>
          <td>${d.descripcion}</td>
        </tr>`;
      tabla.innerHTML += fila;

      const marker = L.marker([d.latitud, d.longitud]).addTo(mapa);
      marker.bindPopup(
        `<strong>${d.nombre_monumento}</strong><br>${d.direccion}`
      );
      markers.push(marker);
    });
  }

  datos = await obtenerDatosDesdeAPI();
  await mostrarResultados(datos);

  // Función para manejar el evento de cancelar
  document.getElementById("cancelar").addEventListener("click", async () => {
    // Limpiar los campos de filtro
    localidadInput.value = "";
    provinciaInput.value = "";
    postalInput.value = "";
    document.getElementById("tipo").value = "";

    // Limpiar los resultados en la tabla y el mapa
    limpiarMapa();

    // Llamar a la función para mostrar todos los datos
    await mostrarResultados(datos);

    // Centrar el mapa en España
    mapa.setView([40.4168, -3.7038], 6);
  });

  // Función para manejar el evento de búsqueda
  buscarBtn.addEventListener("click", async () => {
    console.log("El archivo JavaScript se ha cargado correctamente.");
    limpiarMapa();

    // Obtener los valores de los campos del formulario
    const localidad = localidadInput.value.toLowerCase();
    const provincia = provinciaInput.value.toLowerCase();
    const codigoPostal = postalInput.value;
    const tipo = document.getElementById("tipo").value;

    // Filtrar los resultados basados en los datos cargados
    const resultados = datos.filter((d) => {
      // Depurar ambos valores comparados
      console.log("Valor del tipo:", tipo.toLowerCase());
      console.log("Valor de tipo_monumento:", d.tipo_monumento.toLowerCase());

      return (
        (localidad
          ? d.nombre_localidad.toLowerCase().includes(localidad)
          : true) &&
        (provincia
          ? d.nombre_provincia.toLowerCase().includes(provincia)
          : true) &&
        (codigoPostal ? d.codigo_postal.includes(codigoPostal) : true) &&
        (tipo && tipo.toLowerCase()
          ? d.tipo_monumento.toLowerCase().includes(tipo.toLowerCase())
          : true)
      );
    });

    // Mostrar los resultados en la tabla
    const tabla = document
      .getElementById("tabla-resultados")
      .querySelector("tbody");
    tabla.innerHTML = "";

    if (
      resultados.length === 0 &&
      !localidad &&
      !provincia &&
      !codigoPostal &&
      !tipo
    ) {
      // Si no hay filtros, mostrar todos los datos y centrar el mapa en España
      datos.forEach((d) => {
        const fila = `<tr>
                <td>${d.nombre_monumento}</td>
                <td>${d.tipo_monumento}</td>
                <td>${d.direccion}</td>
                <td>${d.nombre_localidad}</td>
                <td>${d.codigo_postal}</td>
                <td>${d.nombre_provincia}</td>
                <td>${d.descripcion}</td>
            </tr>`;
        tabla.innerHTML += fila;

        const marker = L.marker([d.latitud, d.longitud]).addTo(mapa);
        marker.bindPopup(
          `<strong>${d.nombre_monumento}</strong><br>${d.direccion}`
        );
        markers.push(marker);
      });

      // Centrar el mapa en todos los puntos
      const bounds = markers.map((marker) => marker.getLatLng());
      mapa.fitBounds(bounds); // Ajustar el zoom para mostrar todos los marcadores
    } else {
      // Si hay filtros, mostrar los resultados filtrados
      resultados.forEach((d) => {
        const fila = `<tr>
                <td>${d.nombre_monumento}</td>
                <td>${d.tipo_monumento}</td>
                <td>${d.direccion}</td>
                <td>${d.nombre_localidad}</td>
                <td>${d.codigo_postal}</td>
                <td>${d.nombre_provincia}</td>
                <td>${d.descripcion}</td>
            </tr>`;
        tabla.innerHTML += fila;

        const marker = L.marker([d.latitud, d.longitud]).addTo(mapa);
        marker.bindPopup(
          `<strong>${d.nombre_monumento}</strong><br>${d.direccion}`
        );
        markers.push(marker);
      });

      // Centrar el mapa en todos los puntos
      const bounds = markers.map((marker) => marker.getLatLng());
      mapa.fitBounds(bounds); // Ajustar el zoom para mostrar todos los marcadores
    }
  });

  // Mostrar sugerencias cuando el usuario escribe
  localidadInput.addEventListener("input", () =>
    mostrarSugerencias(
      localidadInput,
      "nombre_localidad",
      "localidad-suggestions"
    )
  );
  provinciaInput.addEventListener("input", () =>
    mostrarSugerencias(
      provinciaInput,
      "nombre_provincia",
      "provincia-suggestions"
    )
  );
  postalInput.addEventListener("input", () =>
    mostrarSugerencias(
      postalInput,
      "codigo_postal",
      "codigo-postal-suggestions"
    )
  );
  // Añadir funcionalidad de ordenación en las cabeceras de la tabla
  const headers = document.querySelectorAll("#tabla-resultados th");
  headers.forEach((header, index) => {
    let orden = "asc"; // Orden inicial
    header.addEventListener("click", () => {
      ordenarTabla(index, orden);
      orden = orden === "asc" ? "desc" : "asc";
    });
  });
});
