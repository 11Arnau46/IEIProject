document.addEventListener("DOMContentLoaded", () => {
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
    const value = input.value.toLowerCase();
    const suggestions = datos
      .map((d) => d[key])
      .filter(
        (v, i, a) => a.indexOf(v) === i && v.toLowerCase().includes(value)
      );
    const suggestionsList = document.getElementById(suggestionsId);
    suggestionsList.innerHTML = "";

    // Muestra las sugerencias solo si hay texto ingresado
    if (value.length > 0) {
      suggestions.forEach((s) => {
        const li = document.createElement("li");
        li.textContent = s;
        li.addEventListener("click", () => {
          input.value = s;
          suggestionsList.innerHTML = "";
          ajustarEspacio(suggestionsList, input);
        });
        suggestionsList.appendChild(li);
      });
    }
    ajustarEspacio(suggestionsList, input);
  }

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

  // Función para manejar el evento de búsqueda
  buscarBtn.addEventListener("click", async () => {
    console.log("El archivo JavaScript se ha cargado correctamente.");
    limpiarMapa();

    // Obtener los valores de los campos del formulario
    const localidad = localidadInput.value.toLowerCase();
    const provincia = provinciaInput.value.toLowerCase();
    const codigoPostal = postalInput.value;
    const tipo = document.getElementById("tipo").value;

    // Llamar a la API con los filtros
    const resultados = await obtenerDatosDesdeAPI({
      localidad,
      provincia,
      codigo_postal: codigoPostal,
      tipo,
    });
    datos = resultados;
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
          `<strong>${d.nomMonumento}</strong><br>${d.direccion}`
        );
        markers.push(marker);
      });

      // Centrar el mapa en España
      mapa.setView([40.4168, -3.7038], 6);
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

      // Centrar el mapa en el primer resultado
      mapa.setView([resultados[0].latitud, resultados[0].longitud], 10);
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
