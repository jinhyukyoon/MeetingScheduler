document.addEventListener('DOMContentLoaded', function() {
    const slots = JSON.parse(document.getElementById('calendar-data').textContent);
    let currentYear = new Date().getFullYear();
    let currentMonth = new Date().getMonth();
    const isAdmin = JSON.parse(document.getElementById('is-admin').textContent);

    window.changeMonth = function(delta) {
        currentMonth += delta;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        } else if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        generateCalendar(currentYear, currentMonth);
    }

    window.generateCalendar = function(year, month) {
        const calendar = document.getElementById('calendar');
        const title = document.getElementById('calendar-title');
        title.textContent = `${year}-${String(month + 1).padStart(2, '0')}`;

        calendar.innerHTML = '';
        const date = new Date(year, month, 1);
        const firstDay = date.getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.classList.add('day');
            calendar.appendChild(emptyCell);
        }

        // Add cells for each day of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('div');
            cell.classList.add('day');
            const header = document.createElement('div');
            header.classList.add('day-header');
            header.textContent = day;
            if (isAdmin) {
                header.classList.add('clickable');
                header.onclick = () => openAdminSetSlotForm(year, month + 1, day);
            }
            cell.appendChild(header);

            const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            if (slots[dateString]) {
                // Sort slots by time
                slots[dateString].sort((a, b) => a.time.localeCompare(b.time));
                slots[dateString].forEach(slot => {
                    const slotDiv = document.createElement('div');
                    slotDiv.classList.add('slot');
                    slotDiv.textContent = `${slot.time} ${slot.reserved ? `(${slot.name})` : ''}`;
                    slotDiv.title = slot.reserved ? 'Reserved' : 'Available';
                    if (slot.reserved) {
                        slotDiv.classList.add('reserved');
                        if (isAdmin) {
                            slotDiv.onclick = () => openAdminCancelForm(slot);
                        } else {
                            slotDiv.onclick = () => openCancelForm(slot.reservation_id);
                        }
                    } else {
                        if (isAdmin) {
                            slotDiv.onclick = () => openAdminRemoveSlotForm(slot, dateString);
                        } else {
                            slotDiv.onclick = () => openReservationForm(dateString, slot.time);
                        }
                    }
                    cell.appendChild(slotDiv);
                });
            }

            calendar.appendChild(cell);
        }
    }

    window.openReservationForm = function(date, time) {
        const datetime = `${date}T${time}`;
        document.getElementById('datetime').value = datetime;
        document.getElementById('reservationModal').style.display = 'block';
    }

    window.openCancelForm = function(reservationId) {
        document.getElementById('cancel_reservation_id').value = reservationId;
        document.getElementById('cancelModal').style.display = 'block';
    }

    window.openAdminCancelForm = function(slot) {
        document.getElementById('admin_cancel_reservation_id').value = slot.reservation_id;
        document.getElementById('adminReservationDetails').innerText = `Name: ${slot.name}\nPhone: ${slot.phone}\nTime: ${slot.time}`;
        document.getElementById('adminCancelModal').style.display = 'block';
    }

    window.openAdminRemoveSlotForm = function(slot, dateString) {
        document.getElementById('admin_remove_slot_id').value = slot.slot_id;
        document.getElementById('adminRemoveSlotTitle').innerText = `Confirm Slot Removal (${dateString})`;
        document.getElementById('adminRemoveSlotDetails').innerText = `Time: ${slot.time}`;
        document.getElementById('adminRemoveSlotModal').style.display = 'block';
    }

    window.openAdminSetSlotForm = function(year, month, day) {
        const date = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        document.getElementById('available_date').value = date;
        document.getElementById('adminSetSlotTitle').innerText = `Set Available Slot (${date})`;
        document.getElementById('adminSetSlotModal').style.display = 'block';
    }

    window.closeModal = function(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    window.toggleEndDate = function() {
        var repeat = document.getElementById("repeat").value;
        var endDateField = document.getElementById("end_date_field");
        if (repeat === "none") {
            endDateField.style.display = "none";
        } else {
            endDateField.style.display = "block";
        }
    }

    window.validateSetSlotForm = function() {
        var repeat = document.getElementById("repeat").value;
        var endDate = document.getElementById("end_date").value;
        if (repeat !== "none" && endDate === "") {
            alert("Please provide an end date for the repetition.");
            return false;
        }
        return true;
    }

    window.cancelReservation = function(reservationId) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/admin/cancel';
        form.style.display = 'none';

        const reservationIdInput = document.createElement('input');
        reservationIdInput.name = 'reservation_id';
        reservationIdInput.value = reservationId;
        form.appendChild(reservationIdInput);

        document.body.appendChild(form);
        form.submit();
    }

    // Initialize the calendar with the current month
    generateCalendar(currentYear, currentMonth);
});
