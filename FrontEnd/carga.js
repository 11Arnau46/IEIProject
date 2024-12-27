document.getElementById('cargar').addEventListener('click', async function () {
    const selectedFuentes = Array.from(document.querySelectorAll('input[name="fuente"]:checked')).map(input => input.value);
    const resultadosDiv = document.getElementById('resultados');
    resultadosDiv.innerHTML = '';

    // Clear files
    try {
        const clearResponse = await fetch('http://localhost:8080/clear_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('Clear files response:', clearResponse.status);
        resultadosDiv.innerHTML += `<p>Archivos limpiados correctamente.</p>`;
    } catch (error) {
        console.error('Error clearing files:', error);
        resultadosDiv.innerHTML += `<p>Error al limpiar los archivos: ${error.message}</p>`;
        return;
    }

    // Execute APIs
    for (const fuente of selectedFuentes) {
        let endpoint;
        if (fuente === 'castilla') {
            endpoint = 'http://localhost:8080/extractor/execute_xml';
        } else if (fuente === 'valenciana') {
            endpoint = 'http://localhost:8080/extractor/execute_csv';
        } else if (fuente === 'euskadi') {
            endpoint = 'http://localhost:8080/extractor/execute_json';
        }

        if (endpoint) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const result = await response.json();
                console.log(`Response for ${fuente}:`, result);
                resultadosDiv.innerHTML += `<p>${fuente}: ${result.message}</p>`;
            } catch (error) {
                console.error(`Error executing API for ${fuente}:`, error);
                resultadosDiv.innerHTML += `<p>${fuente}: Error al ejecutar la API: ${error.message}</p>`;
            }
        }
    }

    // Fetch log summary
    try {
        console.log('Fetching load results...');
        const response = await fetch('http://localhost:8080/load_results');
        console.log('Load results response status:', response.status);

        const logSummary = await response.text();
        console.log('Load results:', logSummary);
        resultadosDiv.innerHTML += `<h2>Resultados de la carga:</h2><pre>${logSummary}</pre>`;
    } catch (error) {
        console.error('Error fetching load results:', error);
        resultadosDiv.innerHTML += `<p>Error al obtener los resultados de la carga: ${error.message}</p>`;
    }
});
