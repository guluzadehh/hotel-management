$(document).ready(function () {
    function displayRooms(data) {
        const room_list = $('#room-list');

        room_list.empty();

        for (const room of data) {
            room_list.append(
                `<div class="room-item p-2 mt-1">
                    <div class="d-flex justify-content-between align-items-center">
                        <h4>Комната ${room['number']}</h4>
                        <p>Кол-во мест: ${room['beds']}</p>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <p>Цена: ${room['price_per_day']} руб.</p>
                        <button type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#roomModal" data-room-id="${room['id']}">Забронировать</button>
                    </div>
                </div>`
            );
        }
    }

    function fetchRooms(url) {
        $.ajax({
            method: 'GET',
            url: url,
            success: function (json) {
                displayRooms(json)
            },
        });
    }

    fetchRooms('/api/rooms/');

    const dateFormatter = (input, date, instance) => {
        const value = moment(date).format('YYYY-MM-DD');
        input.value = value;
    }

    const filterStartPicker = datepicker('.filter-start-datepicker', {
        id: 1,
        formatter: dateFormatter,
        minDate: new Date(),
    });
    const filterEndPicker = datepicker('.filter-end-datepicker', {
        id: 1,
        formatter: dateFormatter,
        minDate: new Date(),
    });

    let url = new URL('http://127.0.0.1:8000/api/rooms/');

    $('.sort').on('click', '.sort-item', function () {
        const order = $(this).attr('data-order');

        if (order) {
            url.searchParams.set('ordering', order);
        }

        fetchRooms(url.toString());
    });

    $('.filter').on('click', '#filter-btn', function () {
        url = new URL('http://127.0.0.1:8000/api/rooms/');

        const { start, end } = filterStartPicker.getRange();

        if (start) {
            const start_date = moment(start).format('YYYY-MM-DD');
            url.searchParams.set('start_date', start_date);
        }

        if (end) {
            const end_date = moment(end).format('YYYY-MM-DD');
            url.searchParams.set('end_date', end_date);
        }

        const beds = $('input[name="beds"]:checked').val();
        if (beds != undefined) {
            if (beds === 'all') url.searchParams.delete('beds')
            else url.searchParams.set('beds', beds);
        }

        const min_price = $('input[name="min_price"]').val();
        const max_price = $('input[name="max_price"]').val();

        if (min_price && min_price > 0) {
            url.searchParams.set('min_price', min_price);
        }

        if (max_price) {
            if (min_price && max_price >= min_price) {
                url.searchParams.set('max_price', max_price);
            }
        }

        fetchRooms(url.toString());
    });

    const roomModal = $('#roomModal');
    const modalBody = roomModal.find('.modal-body');
    let startPicker, endPicker;

    const makeReservedDates = dates => {
        return dates.map(date => {
            const [year, month, day] = [...date];
            return new Date(year, month - 1, day);
        })
    }

    roomModal.on('show.bs.modal', event => {
        const room_id = event.relatedTarget.getAttribute('data-room-id');

        if (typeof room_id === 'undefined') {
            roomModal.find('.btn-reserve').prop('disabled', true);
            return;
        }

        roomModal.find('.btn-reserve').attr('data-room-id', room_id);

        $.ajax({
            method: 'GET',
            url: `/api/rooms/${room_id}/`,
            success: function (json) {
                startPicker = datepicker('.start-datepicker', {
                    id: 2,
                    formatter: dateFormatter,
                    disabledDates: makeReservedDates(json['reserved_dates']),
                    minDate: new Date(),
                });
                endPicker = datepicker('.end-datepicker', {
                    id: 2,
                    formatter: dateFormatter,
                    disabledDates: makeReservedDates(json['reserved_dates']),
                    minDate: new Date(),
                });

                modalBody.find('.room-details').prepend(
                    `<h4>Комната ${json['number']}</h4>
                    <p>Цена за сутку: ${json['price_per_day']} руб.</p>`
                );

            },
        })
    });


    roomModal.on('click', '.btn-reserve', function () {
        const room_id = $(this).attr('data-room-id');
        const { start, end } = startPicker.getRange();

        if (!(start && end)) {
            return;
        }

        const start_date = moment(start).format('YYYY-MM-DD');
        const end_date = moment(end).format('YYYY-MM-DD');

        const csrftoken = getCookie('csrftoken');

        $.ajax({
            method: 'POST',
            url: '/api/reservations/',
            headers: {
                'X-CSRFTOKEN': csrftoken,
            },
            data: {
                'room': room_id,
                'start_date': start_date,
                'end_date': end_date,

            },
            success: () => {
                roomModal.modal('hide');
                new bootstrap.Toast($('.toast')).show();
            },
            error: (xhr) => {
                if (xhr.status === 403) {
                    window.location.href = '/account/login';
                    return;
                }

                const error_msg = xhr.responseJSON['non_field_errors'][0];

                modalBody.find('.room-details').prepend(
                    `<p class="modal-msg text-danger p-2">${error_msg}</p>`
                )
            }
        });
    });

    roomModal.on('hide.bs.modal', function () {
        modalBody.find('.room-details').empty();
        roomModal.find('.btn-reserve').removeAttr('data-room-id');
        startPicker.remove();
        endPicker.remove();
    });
});