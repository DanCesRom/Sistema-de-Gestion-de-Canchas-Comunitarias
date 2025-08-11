window.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('time-blocks');
    const openTime = container.getAttribute('data-open-time');
    const closeTime = container.getAttribute('data-close-time');
    const reserved = JSON.parse(container.getAttribute('data-reserved'));
    const blocks = generateTimeBlocks(openTime, closeTime);

    const selectedDateStr = document.getElementById('selected-day').innerText;
    const selectedDate = new Date(selectedDateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    container.innerHTML = "";

    blocks.forEach(time => {
        const div = document.createElement('div');
        div.className = 'block';
        div.innerText = time;

        // Disable past times if selected date is today or before
        let disableBlock = false;
        if (selectedDate < today) {
            disableBlock = true;
        } else if (selectedDate.getTime() === today.getTime()) {
            // Disable times earlier than current time
            const [h, m] = time.split(':').map(Number);
            const now = new Date();
            if (h < now.getHours() || (h === now.getHours() && m <= now.getMinutes())) {
                disableBlock = true;
            }
        }

        if (reserved.includes(time) || disableBlock) {
            div.classList.add('reserved');
            div.style.cursor = 'not-allowed';
        } else {
            div.classList.add('available');
            div.addEventListener('click', () => handleSelect(div, time));
        }

        container.appendChild(div);
    });
});
