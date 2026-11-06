/**
 * GESTIÓN DE COMPROBANTES - LÓGICA FRONTEND
 * Framework: Bulma CSS 
 * Tecnologías: Fetch API, FormData, Manipulación dinámica de DOM y Modales Bulma
 */

document.addEventListener("DOMContentLoaded", () => {
  // 
  // Referencias a Elementos del DOM
  //
  const formComprobante = document.getElementById("form-comprobante");
  const inputTipo = document.getElementById("input-tipo");
  const optBoleta = document.getElementById("opt-boleta");
  const optFactura = document.getElementById("opt-factura");
  const inputFecha = document.getElementById("input-fecha");
  const inputUsuario = document.getElementById("input-usuario");
  const inputTienda = document.getElementById("input-tienda");
  const inputObservacion = document.getElementById("input-observacion");
  const inputImagen = document.getElementById("input-imagen");
  const previewBox = document.getElementById("preview-box");
  const previewImg = document.getElementById("preview-img");
  const previewFilename = document.getElementById("preview-filename");
  const previewSize = document.getElementById("preview-size");
  const btnRemoverImagen = document.getElementById("btn-remover-imagen");
  const btnLimpiarForm = document.getElementById("btn-limpiar-form");
  const btnSubmit = document.getElementById("btn-submit-comprobante");

  // Tabla y Estado Vacío
  const tbodyComprobantes = document.getElementById("tbody-comprobantes");
  const emptyState = document.getElementById("empty-state");
  const badgeTotalTabla = document.getElementById("badge-total-tabla");
  const btnRefrescarTabla = document.getElementById("btn-refrescar-tabla");

  // Indicadores Dinámicos (Tarjetas y Sidebar)
  const cardTotalRegistros = document.getElementById("card-total-registros");
  const cardTotalTiendas = document.getElementById("card-total-tiendas");
  const cardTotalImagenes = document.getElementById("card-total-imagenes");
  const cardChincha = document.getElementById("card-chincha");
  const cardPisco = document.getElementById("card-pisco");
  const cardIca = document.getElementById("card-ica");
  const sbRegistros = document.getElementById("sb-registros");
  const sbTiendas = document.getElementById("sb-tiendas");
  const sbImagenes = document.getElementById("sb-imagenes");
  const sbNavBadge = document.getElementById("sb-nav-badge");

  // Modales
  const modalImagen = document.getElementById("modal-imagen");
  const modalImgTitulo = document.getElementById("modal-img-titulo");
  const modalImgElement = document.getElementById("modal-img-element");
  const modalImgS3Key = document.getElementById("modal-img-s3key");
  const modalImgLoader = document.getElementById("modal-img-loader");
  const btnDescargarImagen = document.getElementById("btn-descargar-imagen");

  const modalJson = document.getElementById("modal-json");
  const modalJsonTitulo = document.getElementById("modal-json-titulo");
  const modalJsonContent = document.getElementById("modal-json-content");
  const btnCopiarJson = document.getElementById("btn-copiar-json");

  const modalEliminar = document.getElementById("modal-eliminar");
  const modalEliminarDetalle = document.getElementById("modal-eliminar-detalle");
  const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar");

  // Sidebar Móvil
  const appSidebar = document.getElementById("app-sidebar");
  const btnToggleSidebar = document.getElementById("btn-toggle-sidebar");

  // Estado en memoria
  let idParaEliminar = null;
  let comprobantesCache = [];
  let jsonActualParaCopiar = "";

  // 
  // 1. Inicialización de Valores por Defecto
  //
  function inicializarFormulario() {
    // Establecer fecha de hoy en formato YYYY-MM-DD
    const hoy = new Date().toISOString().split("T")[0];
    if (inputFecha) inputFecha.value = hoy;

    // Tipo por defecto: boleta
    seleccionarTipo("boleta");

    // Limpiar imagen seleccionada
    removerImagenSeleccionada();

    if (inputObservacion) inputObservacion.value = "";
    if (inputTienda) inputTienda.value = "Chincha";
    if (inputUsuario && !inputUsuario.value) inputUsuario.value = "Luis Alcala";
  }

  // Segmented control para Boleta / Factura
  function seleccionarTipo(tipo) {
    if (tipo === "factura") {
      inputTipo.value = "factura";
      optFactura.classList.add("is-selected");
      optBoleta.classList.remove("is-selected");
    } else {
      inputTipo.value = "boleta";
      optBoleta.classList.add("is-selected");
      optFactura.classList.remove("is-selected");
    }
  }

  if (optBoleta) optBoleta.addEventListener("click", () => seleccionarTipo("boleta"));
  if (optFactura) optFactura.addEventListener("click", () => seleccionarTipo("factura"));

  // 
  // 2. Manejo de Subida de Imagen y Previsualización Local
  // 
  if (inputImagen) {
    inputImagen.addEventListener("change", (e) => {
      const archivo = e.target.files[0];
      if (!archivo) {
        removerImagenSeleccionada();
        return;
      }

      // Validar extensión
      const extension = archivo.name.toLowerCase().split(".").pop();
      if (!["jpg", "jpeg", "png"].includes(extension)) {
        mostrarToast("Formato no permitido. Solo se aceptan archivos JPG, JPEG o PNG.", "is-danger");
        removerImagenSeleccionada();
        return;
      }

      // Validar tamaño máximo (10 MB)
      if (archivo.size > 10 * 1024 * 1024) {
        mostrarToast("El archivo excede el tamaño máximo permitido (10 MB).", "is-danger");
        removerImagenSeleccionada();
        return;
      }

      // Mostrar preview interactivo
      const reader = new FileReader();
      reader.onload = (event) => {
        previewImg.src = event.target.result;
        previewFilename.textContent = archivo.name;
        const tamKb = (archivo.size / 1024).toFixed(1);
        previewSize.textContent = `${tamKb} KB • Imagen ${extension.toUpperCase()}`;
        previewBox.classList.add("is-visible");
      };
      reader.readAsDataURL(archivo);
    });
  }

  function removerImagenSeleccionada() {
    if (inputImagen) inputImagen.value = "";
    if (previewImg) previewImg.src = "";
    if (previewBox) previewBox.classList.remove("is-visible");
  }

  if (btnRemoverImagen) {
    btnRemoverImagen.addEventListener("click", removerImagenSeleccionada);
  }

  if (btnLimpiarForm) {
    btnLimpiarForm.addEventListener("click", inicializarFormulario);
  }

  //
  // 3. Envío Asíncrono del Formulario (POST /api/comprobantes)
  // 
  if (formComprobante) {
    formComprobante.addEventListener("submit", async (e) => {
      e.preventDefault();

      // Validaciones client-side
      if (!inputFecha.value) {
        mostrarToast("Por favor ingresa la fecha de emisión.", "is-danger");
        inputFecha.focus();
        return;
      }
      if (!inputUsuario.value.trim()) {
        mostrarToast("El campo de usuario es obligatorio.", "is-danger");
        inputUsuario.focus();
        return;
      }
      if (!inputImagen.files || inputImagen.files.length === 0) {
        mostrarToast("Debes seleccionar una imagen del comprobante (JPG o PNG).", "is-danger");
        return;
      }

      const formData = new FormData(formComprobante);

      // Estado de carga en el botón
      btnSubmit.classList.add("is-loading");
      btnSubmit.disabled = true;

      try {
        const respuesta = await fetch("/api/comprobantes", {
          method: "POST",
          body: formData,
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok || !resultado.success) {
          throw new Error(resultado.error || "Ocurrió un error al procesar el comprobante.");
        }

        mostrarToast("¡Comprobante procesado, imagen guardada en S3 y registrado en DynamoDB!", "is-success");
        inicializarFormulario();
        await cargarComprobantes();

        // Desplazar suavemente a la tabla de comprobantes
        const seccionTabla = document.getElementById("seccion-comprobantes");
        if (seccionTabla) {
          seccionTabla.scrollIntoView({ behavior: "smooth" });
        }
      } catch (error) {
        mostrarToast(error.message, "is-danger");
      } finally {
        btnSubmit.classList.remove("is-loading");
        btnSubmit.disabled = false;
      }
    });
  }

  //
  // 4. Carga y Renderizado Dinámico de Comprobantes (GET /api/comprobantes)
  // 
  async function cargarComprobantes() {
    try {
      if (btnRefrescarTabla) btnRefrescarTabla.classList.add("is-loading");

      const respuesta = await fetch("/api/comprobantes");
      const resultado = await respuesta.json();

      if (!respuesta.ok || !resultado.success) {
        throw new Error(resultado.error || "Error al obtener la lista de comprobantes.");
      }

      comprobantesCache = resultado.data || [];
      const resumen = resultado.resumen || {
        total_registros: 0,
        total_tiendas: 0,
        total_imagenes: 0,
        desglose: { Chincha: 0, Pisco: 0, Ica: 0 },
      };

      // 4.1. Actualizar métricas dinámicas (NUNCA fijas)
      actualizarIndicadores(resumen);

      // 4.2. Renderizar filas en la tabla
      renderizarTabla(comprobantesCache);
    } catch (error) {
      console.error("Error al cargar comprobantes:", error);
      mostrarToast(`No se pudo actualizar el listado: ${error.message}`, "is-danger");
    } finally {
      if (btnRefrescarTabla) btnRefrescarTabla.classList.remove("is-loading");
    }
  }

  function actualizarIndicadores(resumen) {
    // Tarjetas principales
    if (cardTotalRegistros) cardTotalRegistros.textContent = resumen.total_registros;
    if (cardTotalTiendas) cardTotalTiendas.textContent = resumen.total_tiendas;
    if (cardTotalImagenes) cardTotalImagenes.textContent = resumen.total_imagenes;

    // Desglose regional
    const desglose = resumen.desglose || {};
    if (cardChincha) cardChincha.textContent = desglose.Chincha || 0;
    if (cardPisco) cardPisco.textContent = desglose.Pisco || 0;
    if (cardIca) cardIca.textContent = desglose.Ica || 0;

    // Indicadores del sidebar
    if (sbRegistros) sbRegistros.textContent = resumen.total_registros;
    if (sbTiendas) sbTiendas.textContent = resumen.total_tiendas;
    if (sbImagenes) sbImagenes.textContent = resumen.total_imagenes;
    if (sbNavBadge) sbNavBadge.textContent = resumen.total_registros;

    // Badge en la cabecera de la tabla
    if (badgeTotalTabla) {
      badgeTotalTabla.textContent = `${resumen.total_registros} ${resumen.total_registros === 1 ? 'registro' : 'registros'}`;
    }
  }

  function renderizarTabla(comprobantes) {
    if (!tbodyComprobantes) return;

    if (!comprobantes || comprobantes.length === 0) {
      tbodyComprobantes.innerHTML = "";
      if (emptyState) emptyState.style.display = "block";
      return;
    }

    if (emptyState) emptyState.style.display = "none";

    const filasHtml = comprobantes.map((c) => {
      const esFactura = (c.tipo || "").toLowerCase() === "factura";
      const badgeClase = esFactura ? "is-factura" : "is-boleta";
      const iconoTipo = esFactura ? "fa-file-invoice-dollar" : "fa-receipt";
      const tipoTexto = esFactura ? "Factura" : "Boleta";
      const correlativo = c.numero_comprobante || (c.datos_textract?.comprobante?.numero_completo) || "S/N";

      // Formatear montos priorizando los datos del comprobante/JSON
      const totalVal = (c.monto_total !== undefined && c.monto_total !== null) ? c.monto_total : (c.datos_textract?.importes?.total || 0);
      const igvVal = (c.igv !== undefined && c.igv !== null) ? c.igv : (c.datos_textract?.importes?.igv || 0);
      const totalNum = parseFloat(totalVal).toFixed(2);
      const igvNum = parseFloat(igvVal).toFixed(2);

      // Fecha de emisión visible en documento vs fecha de registro del formulario
      const fechaEmisionDoc = c.datos_textract?.comprobante?.fecha_emision || c.fecha_emision_documento || c.fecha || "";
      const fechaFormulario = c.fecha || "";
      const mostrarDobleFecha = fechaEmisionDoc && fechaFormulario && (fechaEmisionDoc !== fechaFormulario);

      // Observación
      const observacion = c.observacion ? escapeHtml(c.observacion) : '<span style="color:var(--color-texto-muted); font-style:italic;">Sin observación</span>';

      return `
        <tr>
          <td>
            <div style="display:flex; flex-direction:column; gap:0.2rem;">
              <span class="badge-tipo ${badgeClase}">
                <i class="fa-solid ${iconoTipo}"></i> ${tipoTexto}
              </span>
              <strong style="font-size:0.85rem; color:var(--color-verde-bosque);">${escapeHtml(correlativo)}</strong>
            </div>
          </td>
          <td>
            <div style="line-height:1.25;">
              <strong style="color:var(--color-verde-bosque);">${escapeHtml(fechaEmisionDoc)}</strong>
              ${mostrarDobleFecha ? `<div style="font-size:0.73rem; color:var(--color-texto-muted);" title="Fecha ingresada en el formulario">Reg: ${escapeHtml(fechaFormulario)}</div>` : ''}
            </div>
          </td>
          <td>
            <span style="color:var(--color-texto-principal);">${escapeHtml(c.usuario || "")}</span>
          </td>
          <td>
            <span class="badge-tienda">
              <i class="fa-solid fa-location-dot" style="font-size:0.7rem; color:var(--color-verde-salvia);"></i> ${escapeHtml(c.tienda || "")}
            </span>
          </td>
          <td>
            <div style="line-height:1.2;">
              <strong style="color:var(--color-verde-bosque);">S/ ${totalNum}</strong>
              <div style="font-size:0.74rem; color:var(--color-texto-muted);">IGV: S/ ${igvNum}</div>
            </div>
          </td>
          <td style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(c.observacion || '')}">
            ${observacion}
          </td>
          <td style="text-align: right;">
            <div class="table-actions" style="justify-content: flex-end;">
              <button class="button is-small is-light btn-action btn-ver-imagen" data-id="${c.id}" title="Ver imagen en S3">
                <i class="fa-regular fa-image"></i> <span class="is-hidden-mobile">Imagen</span>
              </button>
              <button class="button is-small is-light btn-action btn-ver-json" data-id="${c.id}" title="Consultar JSON Textract">
                <i class="fa-solid fa-code"></i> <span class="is-hidden-mobile">Ver datos</span>
              </button>
              <button class="button is-small is-danger is-light btn-action btn-eliminar-comprobante" data-id="${c.id}" title="Eliminar comprobante e imagen">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

    tbodyComprobantes.innerHTML = filasHtml;

    // Vincular eventos de las acciones en cada fila
    tbodyComprobantes.querySelectorAll(".btn-ver-imagen").forEach((btn) => {
      btn.addEventListener("click", () => abrirModalImagen(btn.getAttribute("data-id")));
    });

    tbodyComprobantes.querySelectorAll(".btn-ver-json").forEach((btn) => {
      btn.addEventListener("click", () => abrirModalJson(btn.getAttribute("data-id")));
    });

    tbodyComprobantes.querySelectorAll(".btn-eliminar-comprobante").forEach((btn) => {
      btn.addEventListener("click", () => abrirModalEliminar(btn.getAttribute("data-id")));
    });
  }

  // 
  // 5. Modales: Imagen, JSON y Eliminación
  // 

  // 5.1. Modal de Imagen S3
  function abrirModalImagen(id) {
    const item = comprobantesCache.find((c) => c.id === id);
    const tipo = item?.tipo ? item.tipo.toUpperCase() : "COMPROBANTE";
    const correlativo = item?.numero_comprobante || id;

    modalImgTitulo.textContent = `${tipo}: ${correlativo} (Sede ${item?.tienda || ''})`;
    modalImgS3Key.textContent = `Clave S3: ${item?.s3_key || 'No registrada'}`;

    const urlImagen = `/api/comprobantes/${id}/imagen`;
    modalImgLoader.style.display = "block";
    modalImgElement.style.display = "none";
    modalImgElement.src = urlImagen;

    modalImgElement.onload = () => {
      modalImgLoader.style.display = "none";
      modalImgElement.style.display = "block";
    };

    modalImgElement.onerror = () => {
      modalImgLoader.style.display = "none";
      mostrarToast("No se pudo cargar la imagen desde el bucket S3 de Floci.", "is-danger");
    };

    if (btnDescargarImagen) btnDescargarImagen.href = urlImagen;

    abrirModal(modalImagen);
  }

  // 5.2. Modal de JSON (Textract Simulado)
  async function abrirModalJson(id) {
    const item = comprobantesCache.find((c) => c.id === id);
    modalJsonTitulo.textContent = `JSON Textract: ${item?.numero_comprobante || id}`;
    modalJsonContent.textContent = "Obteniendo datos de Textract y DynamoDB...";
    abrirModal(modalJson);

    try {
      const respuesta = await fetch(`/api/comprobantes/${id}/json`);
      const resultado = await respuesta.json();

      if (!respuesta.ok || !resultado.success) {
        throw new Error(resultado.error || "No se pudo recuperar el JSON.");
      }

      const datosCompletos = resultado.datos_textract || resultado.comprobante;
      jsonActualParaCopiar = JSON.stringify(datosCompletos, null, 2);
      modalJsonContent.textContent = jsonActualParaCopiar;
    } catch (error) {
      modalJsonContent.textContent = `Error al consultar JSON: ${error.message}`;
    }
  }

  if (btnCopiarJson) {
    btnCopiarJson.addEventListener("click", () => {
      if (!jsonActualParaCopiar) return;
      navigator.clipboard.writeText(jsonActualParaCopiar).then(() => {
        mostrarToast("JSON copiado al portapapeles", "is-success");
      }).catch(() => {
        mostrarToast("No se pudo copiar automáticamente", "is-danger");
      });
    });
  }

  // 5.3. Modal de Confirmación de Eliminación
  function abrirModalEliminar(id) {
    idParaEliminar = id;
    const item = comprobantesCache.find((c) => c.id === id);
    const tipo = item?.tipo ? item.tipo.toUpperCase() : "COMPROBANTE";
    const numero = item?.numero_comprobante || id;

    modalEliminarDetalle.innerHTML = `
      <div style="background-color: var(--color-beige); padding: 0.65rem 0.85rem; border-radius: 6px;">
        <div><strong>Comprobante:</strong> ${tipo} ${escapeHtml(numero)}</div>
        <div><strong>Tienda / Sede:</strong> ${escapeHtml(item?.tienda || '-')}</div>
        <div><strong>Fecha:</strong> ${escapeHtml(item?.fecha || '-')}</div>
        <div><strong>Total:</strong> S/ ${parseFloat(item?.monto_total || 0).toFixed(2)}</div>
      </div>
    `;

    abrirModal(modalEliminar);
  }

  if (btnConfirmarEliminar) {
    btnConfirmarEliminar.addEventListener("click", async () => {
      if (!idParaEliminar) return;

      btnConfirmarEliminar.classList.add("is-loading");
      btnConfirmarEliminar.disabled = true;

      try {
        const respuesta = await fetch(`/api/comprobantes/${idParaEliminar}`, {
          method: "DELETE",
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok || !resultado.success) {
          throw new Error(resultado.error || "No se pudo eliminar el comprobante.");
        }

        cerrarModal(modalEliminar);
        mostrarToast("Comprobante e imagen eliminados coordinadamente de DynamoDB y S3.", "is-success");
        await cargarComprobantes();
      } catch (error) {
        mostrarToast(error.message, "is-danger");
      } finally {
        btnConfirmarEliminar.classList.remove("is-loading");
        btnConfirmarEliminar.disabled = false;
        idParaEliminar = null;
      }
    });
  }

  // 
  // 6. Helpers de Modales y Utilidades
  // 
  function abrirModal(modal) {
    if (modal) modal.classList.add("is-active");
  }

  function cerrarModal(modal) {
    if (modal) modal.classList.remove("is-active");
  }

  // Botones de cierre y fondos oscuros de modales
  document.querySelectorAll("[data-close-modal]").forEach((elem) => {
    elem.addEventListener("click", () => {
      const modal = elem.closest(".modal");
      if (modal) cerrarModal(modal);
    });
  });

  // Cerrar modal al presionar tecla ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal.is-active").forEach((modal) => cerrarModal(modal));
    }
  });

  // Toggle de sidebar en móviles
  if (btnToggleSidebar && appSidebar) {
    btnToggleSidebar.addEventListener("click", () => {
      appSidebar.classList.toggle("is-open");
    });
  }

  if (btnRefrescarTabla) {
    btnRefrescarTabla.addEventListener("click", () => cargarComprobantes());
  }

  // Notificaciones Toast
  function mostrarToast(mensaje, tipo = "is-success", duracion = 4000) {
    const contenedor = document.getElementById("toast-container");
    if (!contenedor) return;

    const toast = document.createElement("div");
    toast.className = `toast-item ${tipo}`;

    const icono = tipo === "is-success" ? "fa-circle-check" : "fa-circle-xmark";
    toast.innerHTML = `
      <i class="fa-solid ${icono} fa-lg"></i>
      <span style="flex-grow:1;">${escapeHtml(mensaje)}</span>
    `;

    contenedor.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
      toast.style.opacity = "0";
      toast.style.transform = "translateX(50px)";
      setTimeout(() => toast.remove(), 300);
    }, duracion);
  }

  // Escapar caracteres peligrosos en HTML
  function escapeHtml(texto) {
    if (texto === null || texto === undefined) return "";
    return String(texto)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // 
  // 7. Arranque Inicial
  // 
  inicializarFormulario();
  cargarComprobantes();
});
