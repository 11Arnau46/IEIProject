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

  // Función para agregar o quitar el espacio dependiendo de la visibilidad de las sugerencias
  function ajustarEspacio(suggestionsList, formGroup) {
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
          ajustarEspacio(suggestionsList, formGroup);
        });
        suggestionsList.appendChild(li);
      });
    }
    ajustarEspacio(suggestionsList, formGroup);
  }

  // Cargar los datos JSON
  fetch("../Resultados/JSONtoJSON_Corregido.json")
    .then((response) => response.json()) // Convierte la respuesta a un objeto JSON
    .then((data) => {
      datos = data; // Asigna los datos cargados a la variable `datos`
      console.log("Datos cargados:", datos); // Verifica que los datos se han cargado correctamente
    })
    .catch((error) => console.error("Error al cargar el JSON:", error));

  // Función para manejar el evento de búsqueda
  buscarBtn.addEventListener("click", () => {
    console.log("El archivo JavaScript se ha cargado correctamente.");
    limpiarMapa();

    // Obtener los valores de los campos del formulario
    const localidad = localidadInput.value.toLowerCase();
    const provincia = provinciaInput.value.toLowerCase();
    const codigoPostal = postalInput.value;
    const tipo = document.getElementById("tipo").value;

    // Filtrar los datos según los valores de los campos
    const resultados = datos.filter((d) => {
      return (
        (!localidad || d.nomLocalidad.toLowerCase().includes(localidad)) &&
        (!provincia || d.nomProvincia.toLowerCase().includes(provincia)) &&
        (!codigoPostal || d.codigo_postal.includes(codigoPostal)) &&
        (!tipo || d.tipoMonumento === tipo)
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
                <td>${d.nomMonumento}</td>
                <td>${d.tipoMonumento}</td>
                <td>${d.direccion}</td>
                <td>${d.nomLocalidad}</td>
                <td>${d.codigo_postal}</td>
                <td>${d.nomProvincia}</td>
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
                <td>${d.nomMonumento}</td>
                <td>${d.tipoMonumento}</td>
                <td>${d.direccion}</td>
                <td>${d.nomLocalidad}</td>
                <td>${d.codigo_postal}</td>
                <td>${d.nomProvincia}</td>
                <td>${d.descripcion}</td>
            </tr>`;
        tabla.innerHTML += fila;

        const marker = L.marker([d.latitud, d.longitud]).addTo(mapa);
        marker.bindPopup(
          `<strong>${d.nomMonumento}</strong><br>${d.direccion}`
        );
        markers.push(marker);
      });

      // Centrar el mapa en el primer resultado
      mapa.setView([resultados[0].latitud, resultados[0].longitud], 10);
    }
  });

  // Mostrar sugerencias cuando el usuario escribe
  localidadInput.addEventListener("input", () =>
    mostrarSugerencias(localidadInput, "nomLocalidad", "localidad-suggestions")
  );
  provinciaInput.addEventListener("input", () =>
    mostrarSugerencias(provinciaInput, "nomProvincia", "provincia-suggestions")
  );
  postalInput.addEventListener("input", () =>
    mostrarSugerencias(
      postalInput,
      "codigo_postal",
      "codigo-postal-suggestions"
    )
  );
});
