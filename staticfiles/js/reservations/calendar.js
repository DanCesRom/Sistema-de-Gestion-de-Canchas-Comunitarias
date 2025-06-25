let selectedBlocks = [];

window.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('time-blocks');
    const openTime = container.getAttribute('data-open-time');
    const closeTime = container.getAttribute('data-close-time');
    const reserved = JSON.parse(container.getAttribute('data-reserved'));
    const blocks = generateTimeBlocks(openTime, closeTime);

    container.innerHTML = "";

    blocks.forEach(time => {
        const div = document.createElement('div');
        div.className = 'block';
        div.innerText = time;

        if (reserved.includes(time)) {
            div.classList.add('reserved');
        } else {
            div.classList.add('available');
            div.addEventListener('click', () => handleSelect(div, time));
        }

        container.appendChild(div);
    });
});

function generateTimeBlocks(start, end) {
    const result = [];
    let [h, m] = start.split(':').map(Number);
    const [endH, endM] = end.split(':').map(Number);

    while (h < endH || (h === endH && m < endM)) {
        const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
        result.push(time);
        h += 1;  // incrementa 1 hora
    }
    return result;
}

function handleSelect(div, time) {
    if (div.classList.contains('selected')) {
        // Deseleccionar: quita el bloque
        selectedBlocks = selectedBlocks.filter(t => t !== time);
        div.classList.remove('selected');
    } else {
        // Seleccionar: solo si cumple reglas
        // Intentamos agregar el nuevo bloque
        const tempSelection = [...selectedBlocks, time];
        tempSelection.sort();

        if (tempSelection.length > 3) {
            alert("Solo puedes seleccionar hasta 3 horas seguidas.");
            return;
        }

        if (!areConsecutive(tempSelection)) {
            alert("Las horas deben ser consecutivas.");
            return;
        }

        // Todo ok, actualizar selección
        selectedBlocks = tempSelection;
        div.classList.add('selected');
    }

    updateSelectionUI();
    updateForm();
}

function areConsecutive(times) {
    for (let i = 1; i < times.length; i++) {
        const [h1, m1] = times[i - 1].split(':').map(Number);
        const [h2, m2] = times[i].split(':').map(Number);
        const diff = (h2 * 60 + m2) - (h1 * 60 + m1);
        if (diff !== 60) return false;  // debe ser 60 min (1 hora)
    }
    return true;
}

function updateSelectionUI() {
    // Actualiza la UI para marcar/desmarcar los bloques seleccionados
    const container = document.getElementById('time-blocks');
    const divs = container.querySelectorAll('.block.available');

    divs.forEach(div => {
        if (selectedBlocks.includes(div.innerText)) {
            div.classList.add('selected');
        } else {
            div.classList.remove('selected');
        }
    });
}

function updateForm() {
    const btn = document.getElementById('submit-button');

    if (selectedBlocks.length > 0) {
        selectedBlocks.sort();

        // VALIDACIÓN FINAL ANTES DE ENVIAR
        if (!areConsecutive(selectedBlocks)) {
            btn.disabled = true;
            //alert("Las horas seleccionadas deben ser consecutivas.");
            return;
        }

        document.getElementById('start_time').value = selectedBlocks[0];
        const [h, m] = selectedBlocks[selectedBlocks.length - 1].split(':').map(Number);
        let endH = h + 1;
        let endM = m;
        if (endH === 24) endH = 0;

        document.getElementById('end_time').value = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`;
        btn.disabled = false;
    } else {
        btn.disabled = true;
        document.getElementById('start_time').value = '';
        document.getElementById('end_time').value = '';
    }
}
function changeDay(offset) {
    const current = document.getElementById('selected-day').innerText;
    const newDate = new Date(current);
    newDate.setDate(newDate.getDate() + offset);
    const year = newDate.getFullYear();
    const month = String(newDate.getMonth() + 1).padStart(2, '0');
    const day = String(newDate.getDate()).padStart(2, '0');
    window.location.href = '?date=' + year + '-' + month + '-' + day;
}
